#!/usr/bin/env python3
import argparse
from pathlib import Path
import re
import sys
import urllib.request

URL = "https://download.unimus.net/unimus/Changelog.txt"
VERSION_PATTERN = r"\d+\.\d+\.\d+(?:-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)?"

def get_changelog(url=URL):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode('utf-8-sig')

def parse_version(content, target_version=None):
    # Split content by lines
    lines = content.splitlines()
    
    # Regex to find version headers like "= Version 2.8.0 ="
    version_regex = re.compile(rf"^=\s+Version ({VERSION_PATTERN})\s+=$")
    
    found_version = None
    changelog_lines = []
    capturing = False
    
    for line in lines:
        match = version_regex.fullmatch(line.strip())
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

def fetch_release(product="server", channel="stable", target_version=None):
    directory = "unimus" if product == "server" else "unimus-core"
    if channel == "dev":
        directory += "-dev"
    base_url = f"https://download.unimus.net/{directory}"

    if channel == "dev":
        filename = "Unimus.dev.version" if product == "server" else "Unimus-Core.dev.version"
        version = get_changelog(f"{base_url}/{filename}").strip()
        if not re.fullmatch(VERSION_PATTERN, version) or len(version) > 128:
            raise ValueError(f"Invalid development version: {version!r}")
        if target_version and target_version != version:
            raise ValueError(f"Current development version is {version}, not {target_version}")

        content = get_changelog(f"{base_url}/Changelog.txt")
        _, notes = parse_version(content, version)
        if notes is None:
            _, notes = parse_version(content, version.split("-", 1)[0])
    else:
        content = get_changelog(f"{base_url}/Changelog.txt")
        version, notes = parse_version(content, target_version)
        if version and "-" in version:
            raise ValueError(f"Unexpected prerelease version in stable changelog: {version}")

    if not version or not notes:
        raise ValueError(f"No changelog found for {product} {target_version or version or channel}")
    return version, format_changelog(notes)

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
    parser = argparse.ArgumentParser(description="Fetch Unimus Server or Core release notes.")
    parser.add_argument("version", nargs="?", help="Version to select (defaults to latest)")
    parser.add_argument("--product", choices=("server", "core"), default="server")
    parser.add_argument("--channel", choices=("stable", "dev"), default="stable")
    parser.add_argument("--notes-file", type=Path, help="Write Markdown release notes to this file")
    parser.add_argument("--github-output", type=Path, help="Append version to a GitHub step output file")
    args = parser.parse_args()

    try:
        version, notes = fetch_release(args.product, args.channel, args.version)
        if args.notes_file:
            args.notes_file.write_text(notes + "\n", encoding="utf-8")
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as output:
                output.write(f"version={version}\n")
    except (OSError, ValueError) as exc:
        print(f"Error fetching release: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"VERSION={version}")
    print("<<EOF")
    print(notes)
    print("EOF")

if __name__ == "__main__":
    main()
