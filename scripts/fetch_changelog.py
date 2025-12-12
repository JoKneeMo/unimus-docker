#!/usr/bin/env python3
import urllib.request
import re
import sys

URL = "https://download.unimus.net/unimus/Changelog.txt"

def get_changelog():
    try:
        with urllib.request.urlopen(URL) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching changelog: {e}", file=sys.stderr)
        sys.exit(1)

def parse_latest_version(content):
    # Split content by lines
    lines = content.splitlines()
    
    # Regex to find version headers like "= Version 2.8.0 ="
    version_regex = re.compile(r"^= Version (\d+\.\d+\.\d+) =$")
    
    latest_version = None
    changelog_lines = []
    capturing = False
    
    for line in lines:
        match = version_regex.match(line)
        if match:
            if latest_version is None:
                # Found the first (latest) version
                latest_version = match.group(1)
                capturing = True
                continue
            else:
                # Found the next version header, stop capturing
                break
        
        if capturing:
            changelog_lines.append(line)
            
    if latest_version:
        # Clean up leading/trailing empty lines from changelog
        changelog_text = "\n".join(changelog_lines).strip()
        return latest_version, changelog_text
    else:
        return None, None

def main():
    content = get_changelog()
    version, notes = parse_latest_version(content)
    
    if version:
        print(f"VERSION={version}")
        # Escape newlines for GitHub Actions output if needed, 
        # but for now let's just print a delimiter for the body
        print("<<EOF")
        print(notes)
        print("EOF")
    else:
        print("No version found", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
