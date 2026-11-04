#!/usr/bin/env python3
"""Reject binaries that require a newer macOS than the package advertises."""
import re
import subprocess
import sys


def minimum_versions(load_commands):
    versions = []
    for command in re.split(r"Load command \d+", load_commands):
        if re.search(r"\bcmd LC_BUILD_VERSION\b", command):
            match = re.search(r"\bminos (\d+(?:\.\d+){0,2})", command)
        elif re.search(r"\bcmd LC_VERSION_MIN_MACOSX\b", command):
            match = re.search(r"\bversion (\d+(?:\.\d+){0,2})", command)
        else:
            continue
        if match:
            versions.append(match.group(1))
    if not versions:
        raise ValueError("No macOS deployment target found in Mach-O load commands")
    return versions


def version_tuple(value):
    parts = tuple(map(int, value.split(".")))
    return parts + (0,) * (3 - len(parts))


def verify(load_commands, advertised):
    versions = minimum_versions(load_commands)
    for version in versions:
        if version_tuple(version) > version_tuple(advertised):
            raise ValueError(f"Executable requires macOS {version}, package advertises {advertised}")
    return versions


if __name__ == "__main__":
    binary, architecture, advertised = sys.argv[1:]
    result = subprocess.run(
        ["otool", "-arch", architecture, "-l", binary],
        check=True, text=True, capture_output=True,
    )
    try:
        versions = verify(result.stdout, advertised)
    except ValueError as error:
        sys.exit(str(error))
    print(f"{architecture}: executable minimum {', '.join(versions)} <= package {advertised}")
