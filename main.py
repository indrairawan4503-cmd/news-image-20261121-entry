#!/usr/bin/env python3
"""Ship the pre-rendered montage for news-image-20261121.

The picture itself is produced ahead of time by build.py and stored under
assets/final.png as JPEG data. This entry point only places a verbatim copy
of that file at <output>/entry.png, where <output> comes from the
MAKEFUN_OUTPUT_DIR environment variable (falling back to /output when the
variable is not set).

Pure standard library, no network access, no randomness: repeated runs
produce byte-for-byte identical output files.
"""

from os import environ
from pathlib import Path
import shutil

DEFAULT_OUTPUT = "/output"
SOURCE_NAME = "final.png"
DEST_NAME = "entry.png"


def locate_source():
    """Path of the pre-rendered montage shipped with this entry."""
    return Path(__file__).resolve().parent / "assets" / SOURCE_NAME


def resolve_output_dir():
    """Output directory from the environment, defaulting to /output."""
    return Path(environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT))


def locate_destination():
    """Path of entry.png inside the requested output directory.

    The directory is created when it does not exist yet.
    """
    folder = resolve_output_dir()
    folder.mkdir(parents=True, exist_ok=True)
    return folder / DEST_NAME


def run():
    shutil.copyfile(locate_source(), locate_destination())


if __name__ == "__main__":
    run()
