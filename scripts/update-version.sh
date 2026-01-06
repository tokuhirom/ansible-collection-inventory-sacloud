#!/bin/bash
set -e

# This script is called by tagpr to update version in files
# Usage: update-version.sh <new-version>
# Example: update-version.sh 0.0.6

NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
  echo "Error: Version number required"
  echo "Usage: $0 <version>"
  exit 1
fi

# Remove 'v' prefix if present
NEW_VERSION="${NEW_VERSION#v}"

echo "Updating version to $NEW_VERSION"

# Update galaxy.yml
sed -i.bak "s/version: \".*\"/version: \"$NEW_VERSION\"/" galaxy.yml
rm -f galaxy.yml.bak

# Update README.md - replace version in the release download URL
# This regex matches patterns like: v0.0.5/tokuhirom-sacloud-0.0.5.tar.gz
sed -i.bak "s|releases/download/v[0-9]*\.[0-9]*\.[0-9]*/tokuhirom-sacloud-[0-9]*\.[0-9]*\.[0-9]*\.tar\.gz|releases/download/v${NEW_VERSION}/tokuhirom-sacloud-${NEW_VERSION}.tar.gz|" README.md
rm -f README.md.bak

echo "Version updated successfully"
echo "- galaxy.yml: $NEW_VERSION"
echo "- README.md: v$NEW_VERSION download URL"
