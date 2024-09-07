#!/bin/bash

# Check if a target domain is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <TARGET_DOMAIN>"
    exit 1
fi

TARGET_DOMAIN=$1
TARGET_FOLDER="${TARGET_DOMAIN//./_}"

# Create target directory
mkdir -p "$TARGET_FOLDER"

# Output files
ASSETFINDER_FILE="$TARGET_FOLDER/assetfinder.txt"
SUBFINDER_FILE="$TARGET_FOLDER/subfinder.txt"
CRT_FILE="$TARGET_FOLDER/crt.txt"
WAYBACK_FILE="$TARGET_FOLDER/waybacksubs.txt"
MANUAL_FILE="$TARGET_FOLDER/manualsub.txt"
SUBS_FILE="$TARGET_FOLDER/subs.txt"

# Create or clear output files
> $ASSETFINDER_FILE
> $SUBFINDER_FILE
> $CRT_FILE
> $WAYBACK_FILE
> $MANUAL_FILE
> $SUBS_FILE

# Finding Subdomains

# assetfinder
echo "Running assetfinder..."
assetfinder -subs-only $TARGET_DOMAIN >> $ASSETFINDER_FILE

# subfinder
echo "Running subfinder..."
subfinder -d $TARGET_DOMAIN >> $SUBFINDER_FILE

# crt.sh
echo "Fetching subdomains from crt.sh..."
curl https://crt.sh/?q=$TARGET_DOMAIN | grep -oE '[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' >> $CRT_FILE
sort -u -o $CRT_FILE $CRT_FILE

# Wayback URLs
echo "Fetching subdomains from Wayback URLs..."
curl -s "http://web.archive.org/cdx/search/cdx?url=*.${TARGET_DOMAIN}/*&output=text&fl=original&collapse=urlkey" | \
    sed -e 's_https*://__' -e "s/\/.*//" | sed 's/www\.//g' | sed 's/:80//g' | sort -u | tee $WAYBACK_FILE

# Manual subdomains
echo ""
echo "##############################################################"
echo "Please add any manual subdomains you have (e.g., from Shodan or Censys) to $MANUAL_FILE."
echo "If you don't have any, press Enter within 10 seconds to continue."
echo "##############################################################"
echo ""

# Read with a 10-second timeout
read -t 10 -p "Add manual subdomains and press Enter to continue, or wait for the timeout: " 

# Merge and sort all subdomains
echo "Merging and sorting all subdomains..."
touch $SUBS_FILE
cat $ASSETFINDER_FILE | anew $SUBS_FILE
cat $SUBFINDER_FILE | anew $SUBS_FILE
cat $CRT_FILE | anew $SUBS_FILE
cat $WAYBACK_FILE | anew $SUBS_FILE
cat $MANUAL_FILE | anew $SUBS_FILE
sort -u -o $SUBS_FILE $SUBS_FILE

echo "Subdomain discovery completed. Results saved in $TARGET_FOLDER."

# Banner for live subdomain checks
echo ""
echo "##############################################################"
echo "Subdomain discovery is complete."
echo "Now, it's time to get live subdomains. Run the following commands:"
echo ""
echo "httpx -list $SUBS_FILE -o $TARGET_FOLDER/livesubs.txt"
echo "httpx -status-code -title -tech-detect -list $TARGET_FOLDER/livesubs.txt"
echo "##############################################################"
echo ""
