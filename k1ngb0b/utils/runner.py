"""
Async subprocess runner for executing external tools.
"""

import asyncio
import os
import signal
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
import subprocess


@dataclass
class RunResult:
    """Result of a command execution."""
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    duration: float = 0.0

    @property
    def success(self) -> bool:
        """Check if the command succeeded."""
        return self.returncode == 0 and not self.timed_out

    @property
    def output(self) -> str:
        """Get combined stdout and stderr."""
        return self.stdout + self.stderr

    def lines(self) -> List[str]:
        """Get stdout as lines, filtering empty ones."""
        return [line.strip() for line in self.stdout.splitlines() if line.strip()]


class AsyncRunner:
    """Async subprocess runner with timeout and cleanup support."""

    def __init__(
        self,
        timeout: int = 120,
        max_concurrent: int = 10,
        env: Optional[Dict[str, str]] = None
    ):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.env = env or {}
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._processes: List[asyncio.subprocess.Process] = []

    async def _get_semaphore(self) -> asyncio.Semaphore:
        """Get or create the semaphore for concurrency control."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        return self._semaphore

    def _build_env(self) -> Dict[str, str]:
        """Build the environment for subprocess."""
        env = os.environ.copy()
        env.update(self.env)
        return env

    async def run(
        self,
        cmd: List[str],
        timeout: Optional[int] = None,
        cwd: Optional[Path] = None,
        input_data: Optional[str] = None
    ) -> RunResult:
        """Run a command asynchronously with timeout."""
        import time
        start_time = time.time()

        timeout = timeout or self.timeout
        timed_out = False

        try:
            semaphore = await self._get_semaphore()
            async with semaphore:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    stdin=asyncio.subprocess.PIPE if input_data else None,
                    cwd=cwd,
                    env=self._build_env(),
                    start_new_session=True  # Allows killing process group
                )

                self._processes.append(process)

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input_data.encode() if input_data else None),
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    timed_out = True
                    await self._kill_process(process)
                    stdout, stderr = b'', b'Timeout exceeded'

                self._processes.remove(process)

        except FileNotFoundError:
            return RunResult(
                command=cmd,
                returncode=127,
                stdout='',
                stderr=f"Command not found: {cmd[0]}",
                timed_out=False,
                duration=time.time() - start_time
            )
        except Exception as e:
            return RunResult(
                command=cmd,
                returncode=1,
                stdout='',
                stderr=str(e),
                timed_out=False,
                duration=time.time() - start_time
            )

        return RunResult(
            command=cmd,
            returncode=process.returncode if process.returncode is not None else 1,
            stdout=stdout.decode('utf-8', errors='replace') if isinstance(stdout, bytes) else stdout,
            stderr=stderr.decode('utf-8', errors='replace') if isinstance(stderr, bytes) else stderr,
            timed_out=timed_out,
            duration=time.time() - start_time
        )

    async def _kill_process(self, process: asyncio.subprocess.Process) -> None:
        """Kill a process and its children."""
        if process.returncode is not None:
            return

        try:
            # Try to kill the process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            await asyncio.sleep(0.5)

            if process.returncode is None:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                process.terminate()
                await asyncio.sleep(0.2)
                if process.returncode is None:
                    process.kill()
            except Exception:
                pass

    async def run_tool(
        self,
        tool_name: str,
        args: List[str],
        timeout: Optional[int] = None,
        cwd: Optional[Path] = None
    ) -> RunResult:
        """Run a tool by name, looking up its binary path."""
        binary = shutil.which(tool_name)
        if not binary:
            return RunResult(
                command=[tool_name] + args,
                returncode=127,
                stdout='',
                stderr=f"Tool '{tool_name}' not found in PATH",
                timed_out=False,
                duration=0.0
            )

        return await self.run([binary] + args, timeout=timeout, cwd=cwd)

    async def run_many(
        self,
        commands: List[List[str]],
        timeout: Optional[int] = None
    ) -> List[RunResult]:
        """Run multiple commands concurrently."""
        tasks = [self.run(cmd, timeout=timeout) for cmd in commands]
        return await asyncio.gather(*tasks)

    async def cleanup(self) -> None:
        """Kill all running processes."""
        for process in self._processes:
            await self._kill_process(process)
        self._processes.clear()


def run_sync(
    cmd: List[str],
    timeout: int = 120,
    cwd: Optional[Path] = None,
    capture: bool = True
) -> RunResult:
    """Run a command synchronously (blocking)."""
    import time
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return RunResult(
            command=cmd,
            returncode=result.returncode,
            stdout=result.stdout or '',
            stderr=result.stderr or '',
            timed_out=False,
            duration=time.time() - start_time
        )
    except subprocess.TimeoutExpired:
        return RunResult(
            command=cmd,
            returncode=124,
            stdout='',
            stderr='Timeout exceeded',
            timed_out=True,
            duration=time.time() - start_time
        )
    except FileNotFoundError:
        return RunResult(
            command=cmd,
            returncode=127,
            stdout='',
            stderr=f"Command not found: {cmd[0]}",
            timed_out=False,
            duration=time.time() - start_time
        )
    except Exception as e:
        return RunResult(
            command=cmd,
            returncode=1,
            stdout='',
            stderr=str(e),
            timed_out=False,
            duration=time.time() - start_time
        )


# Default runner instance
_default_runner: Optional[AsyncRunner] = None


def get_runner(
    timeout: int = 120,
    max_concurrent: int = 10
) -> AsyncRunner:
    """Get or create a default runner instance."""
    global _default_runner
    if _default_runner is None:
        _default_runner = AsyncRunner(timeout=timeout, max_concurrent=max_concurrent)
    return _default_runner
