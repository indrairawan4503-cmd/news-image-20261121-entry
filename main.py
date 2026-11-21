#!/usr/bin/env python3
"""Entry program for make.fun bounty news-image-20261121 (variant A).

Writes the pre-rendered photo-montage image (assets/final.png, JPEG bytes)
to the output directory as entry.png. Standard library only, no network,
no randomness: the copy is byte-identical on every run.
"""
import os
import shutil


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "assets", "final.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)


if __name__ == "__main__":
    main()
