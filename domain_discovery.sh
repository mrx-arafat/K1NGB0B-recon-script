#!/bin/bash

# Check if a target domain is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <TARGET_DOMAIN>"
    exit 1
fi

TARGET_DOMAIN=$1

# Output files
ASSETFINDER_FILE="assetfinder.txt"
SUBFINDER_FILE="subfinder.txt"
CRT_FILE="crt.txt"
WAYBACK_FILE="waybacksubs.txt"
MANUAL_FILE="manualsub.txt"
SUBS_FILE="subs.txt"

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

# Manual subdomains (This needs manual intervention to add subdomains)
echo "Please add any manual subdomains to $MANUAL_FILE, then press Enter to continue."
read

# Merge and sort all subdomains
echo "Merging and sorting all subdomains..."
touch $SUBS_FILE
cat $ASSETFINDER_FILE | anew $SUBS_FILE
cat $SUBFINDER_FILE | anew $SUBS_FILE
cat $CRT_FILE | anew $SUBS_FILE
cat $WAYBACK_FILE | anew $SUBS_FILE
cat $MANUAL_FILE | anew $SUBS_FILE
sort -u -o $SUBS_FILE $SUBS_FILE

echo "Subdomain discovery completed. Results saved in $SUBS_FILE."
