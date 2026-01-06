#!/bin/bash
set -e

# This script is called by tagpr to update version in files
# tagpr passes version info via environment variables:
# - TAGPR_CURRENT_VERSION: Current version
# - TAGPR_NEXT_VERSION: Next version to update to

if [ -z "$TAGPR_NEXT_VERSION" ]; then
  echo "Error: TAGPR_NEXT_VERSION environment variable not set"
  echo "This script should be called by tagpr"
  exit 1
fi

# Remove 'v' prefix if present
NEXT_VERSION="${TAGPR_NEXT_VERSION#v}"

echo "Updating version from ${TAGPR_CURRENT_VERSION} to ${NEXT_VERSION}"

# Update galaxy.yml
sed -i.bak "s/version: \".*\"/version: \"${NEXT_VERSION}\"/" galaxy.yml
rm -f galaxy.yml.bak

# Update README.md - replace version in the release download URL
# This regex matches patterns like: v0.0.5/tokuhirom-sacloud-0.0.5.tar.gz
sed -i.bak "s|releases/download/v[0-9]*\.[0-9]*\.[0-9]*/tokuhirom-sacloud-[0-9]*\.[0-9]*\.[0-9]*\.tar\.gz|releases/download/v${NEXT_VERSION}/tokuhirom-sacloud-${NEXT_VERSION}.tar.gz|" README.md
rm -f README.md.bak

echo "Version updated successfully"
echo "- galaxy.yml: ${NEXT_VERSION}"
echo "- README.md: v${NEXT_VERSION} download URL"
