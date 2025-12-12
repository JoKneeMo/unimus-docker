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

def parse_version(content, target_version=None):
    # Split content by lines
    lines = content.splitlines()
    
    # Regex to find version headers like "= Version 2.8.0 ="
    version_regex = re.compile(r"^= Version (\d+\.\d+\.\d+) =$")
    
    found_version = None
    changelog_lines = []
    capturing = False
    
    for line in lines:
        match = version_regex.match(line)
        if match:
            match_version = match.group(1)
            
            if capturing:
                # We hit the next version header, stop capturing
                break
            
            if target_version:
                if match_version == target_version:
                    found_version = match_version
                    capturing = True
            else:
                if found_version is None:
                    found_version = match_version
                    capturing = True
            
            continue
        
        if capturing:
            changelog_lines.append(line)
            
    if found_version:
        # Clean up leading/trailing empty lines from changelog
        changelog_text = "\n".join(changelog_lines).strip()
        return found_version, changelog_text
    else:
        return None, None

def format_changelog(text):
    lines = text.splitlines()
    formatted_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append("")
            continue
            
        # Headers
        if line.endswith(":") and not line.startswith(" "):
            # Top level header
            formatted_lines.append(f"# {stripped}")
        elif line.endswith(":") and line.startswith("  ") and not stripped.startswith("-") and "ISSUE" not in stripped:
            # Sub level header, making them a list because usually has ul sub-items
            formatted_lines.append(f"- {stripped}")
        # Known Issues specific formatting
        elif "ISSUE:" in stripped:
            formatted_lines.append(f"- **ISSUE**: {stripped.replace('ISSUE:', '').strip()}")
        elif "WORKAROUND:" in stripped:
            formatted_lines.append(f"    *WORKAROUND*: {stripped.replace('WORKAROUND:', '').strip()}")
        elif "STATUS:" in stripped:
            formatted_lines.append(f"    *STATUS*: {stripped.replace('STATUS:', '').strip()}")
        # Unordered list items
        elif stripped.startswith("-"):
            formatted_lines.append(line) # Already a ul item
        else:
            # Regular text line, make it a ul
            formatted_lines.append(f"- {stripped}")

    return "\n".join(formatted_lines)

def main():
    target_version = None
    if len(sys.argv) > 1:
        target_version = sys.argv[1]

    content = get_changelog()
    version, notes = parse_version(content, target_version)
    
    if version:
        formatted_notes = format_changelog(notes)
        print(f"VERSION={version}")
        print("<<EOF")
        print(formatted_notes)
        print("EOF")
    else:
        if target_version:
            print(f"Version {target_version} not found in changelog", file=sys.stderr)
        else:
            print("No version found", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
