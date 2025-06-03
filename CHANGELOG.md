# Changelog

All notable changes to the K1NGB0B Recon Script project will be documented in this file.

## [2.0.0] - 2024-01-XX

### Added
- Complete rewrite from Bash to Python for better maintainability
- Modular architecture with separate modules for different functionalities
- Asynchronous subdomain discovery for improved performance
- Configuration file support (YAML)
- Comprehensive error handling and logging
- Progress tracking with visual indicators
- JSON and text report generation
- Unit tests for core functionality
- One-click installation script
- Professional project structure
- Type hints throughout the codebase
- Concurrent processing for faster execution

### Changed
- Migrated from Bash script to Python application
- Improved output organization with structured directories
- Enhanced user interface with colored output and progress bars
- Better domain validation and sanitization
- More robust tool availability checking

### Improved
- Code organization and maintainability
- Error handling and user feedback
- Documentation and examples
- Installation process
- Configuration management

### Technical Details
- **Author**: mrx-arafat (K1NGB0B)
- **Language**: Python 3.8+
- **Architecture**: Modular, object-oriented design
- **Async Support**: Full async/await implementation
- **Testing**: Unit tests with pytest
- **Configuration**: YAML-based configuration system
- **Logging**: Structured logging with colored output
- **Dependencies**: Modern Python packages with proper version management

## [1.0.0] - Original Bash Script

### Features
- Basic subdomain discovery using multiple tools
- Simple output to text files
- Manual subdomain input support
- Live subdomain verification with httpx

### Tools Integrated
- assetfinder
- subfinder
- crt.sh (Certificate Transparency)
- Wayback Machine
- httpx for live verification
