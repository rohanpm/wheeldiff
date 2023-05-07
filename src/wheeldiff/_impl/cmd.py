import argparse
import difflib
import filecmp
import logging
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from collections import namedtuple
from enum import Enum, auto

import wheel_filename

LOG = logging.getLogger("wheeldiff")


class ContentType(Enum):
    CONTENT = auto()


class DiffType(Enum):
    LEFT_ONLY = auto()
    RIGHT_ONLY = auto()
    TEXT_DIFFERS = auto()
    BINARY_DIFFERS = auto()


Record = namedtuple(
    "Record",
    [
        "path",
        "diff_type",
    ],
)


def is_text(path: str) -> bool:
    try:
        pathlib.Path(path).read_text(errors="strict")
        return True
    except:
        LOG.debug("not text? %s", path, exc_info=True)
        return False


def normalize(root: str, version: str, version_in_content: bool):
    LOG.debug("Normalizing under %s (version=%s)", root, version)

    version_re = re.compile(
        rf"""
          (^|[-_/'"\s])         # word boundary prior to version
          {re.escape(version)}  # the version
          ($|[-_/'"\s])         # word boundary after version
        """,
        re.MULTILINE | re.VERBOSE,
    )

    for entry in os.scandir(root):
        path = pathlib.Path(entry.path)

        if version in entry.name:
            new_name = entry.name.replace(version, "$VERSION")
            path = path.parent / new_name
            LOG.debug("Renaming: %s => %s", entry.path, path)
            shutil.move(entry.path, path)

        if entry.is_dir():
            normalize(str(path), version, version_in_content)
        elif is_text(path) and version_in_content:
            content = path.read_text()
            new_content = version_re.sub(r"\1$VERSION\2", content)
            if content != new_content:
                LOG.debug("Rewrote version in %s", path)
                path.write_text(new_content)


class UnpackedWheel:
    def __init__(self, filename: str, normalize_version_in_content: bool):
        self.filename = filename
        self.filename_parsed = wheel_filename.parse_wheel_filename(filename)
        self.normalize_version_in_content = normalize_version_in_content
        self.tempdir = tempfile.TemporaryDirectory(suffix="wheeldiff")

    def __enter__(self):
        out = self.tempdir.__enter__()

        try:
            subprocess.run(
                ["wheel", "unpack", "--dest", out, self.filename],
                check=True,
                capture_output=True,
            )
            normalize(
                out,
                version=self.filename_parsed.version,
                version_in_content=self.normalize_version_in_content,
            )
            return out
        except:
            self.tempdir.__exit__(*sys.exc_info())
            raise

    def __exit__(self, exc, value, tb):
        self.tempdir.__exit__(exc, value, tb)


class Command:
    def __init__(self, wheel1: str, wheel2: str, ignore: list):
        self.wheel1 = wheel1
        self.wheel2 = wheel2
        self.ignore = ignore

    @classmethod
    def from_args(cls, args: argparse.Namespace):
        ignore = set(",".join(args.ignore).split(","))
        ignore = ignore - set(",".join(args.no_ignore).split(","))
        LOG.debug("Effective ignore: %s", ignore)
        return cls(
            wheel1=args.wheel1,
            wheel2=args.wheel2,
            ignore=list(ignore),
        )

    def diff(self, dir1: str, dir2: str, accum: list, prefix=""):
        cmp = filecmp.dircmp(dir1, dir2, ignore=[])
        for name in cmp.left_only:
            accum.append(
                Record(
                    path=prefix + name,
                    diff_type=DiffType.LEFT_ONLY,
                )
            )
        for name in cmp.right_only:
            accum.append(
                Record(
                    path=prefix + name,
                    diff_type=DiffType.RIGHT_ONLY,
                )
            )
        for name in cmp.diff_files:
            path1 = os.path.join(dir1, name)
            path2 = os.path.join(dir2, name)
            if "record" in self.ignore and path1.endswith(".dist-info/RECORD"):
                # FIXME: this should be based more on a standard and should be
                # less of a guess
                continue
            accum.append(
                Record(
                    path=prefix + name,
                    diff_type=DiffType.TEXT_DIFFERS
                    if is_text(path1) and is_text(path2)
                    else DiffType.BINARY_DIFFERS,
                )
            )
        for subdir in cmp.common_dirs:
            sub1 = os.path.join(dir1, subdir)
            sub2 = os.path.join(dir2, subdir)
            self.diff(sub1, sub2, accum, f"{prefix}{subdir}/")

    def print_unified_diff(self, dir1: str, dir2: str, relative_path: str):
        path1 = os.path.join(dir1, relative_path)
        path2 = os.path.join(dir2, relative_path)
        lines1 = open(path1).readlines()
        lines2 = open(path2).readlines()
        sys.stdout.writelines(
            difflib.unified_diff(
                lines1,
                lines2,
                fromfile=f"{self.wheel1}/{relative_path}",
                tofile=f"{self.wheel2}/{relative_path}",
            )
        )

    def run(self):
        LOG.debug("diff %s vs %s", self.wheel1, self.wheel2)
        unpack_opts = dict(normalize_version_in_content=("version" in self.ignore))

        with UnpackedWheel(self.wheel1, **unpack_opts) as unpacked1:
            with UnpackedWheel(self.wheel2, **unpack_opts) as unpacked2:
                accum = []
                self.diff(unpacked1, unpacked2, accum)

                LOG.debug("Accumulated differences: %s", accum)

                for record in accum:
                    if record.diff_type == DiffType.LEFT_ONLY:
                        print(f"Only in {self.wheel1}: {record.path}")
                    elif record.diff_type == DiffType.RIGHT_ONLY:
                        print(f"Only in {self.wheel2}: {record.path}")
                    elif record.diff_type == DiffType.BINARY_DIFFERS:
                        print(f"Binary file differs: {record.path}")
                    elif record.diff_type == DiffType.TEXT_DIFFERS:
                        self.print_unified_diff(unpacked1, unpacked2, record.path)

        sys.exit(0 if not accum else 2)


def entry_point():
    p = argparse.ArgumentParser(description="Show differences between wheels")
    p.add_argument("wheel1")
    p.add_argument("wheel2")

    p.add_argument("--debug", action="store_true", help="Enable verbose logging")

    p.add_argument(
        "--ignore",
        action="append",
        default=[],
        help=("Ignore differences of these types " "(options: version, record)"),
        metavar="type1[,type2[,...]]",
    )
    p.add_argument(
        "--no-ignore",
        action="append",
        default=[],
        help="Inverse of `--ignore'",
        metavar="type1[,type2[,...]]",
    )

    parsed = p.parse_args()

    if parsed.debug:
        logging.basicConfig(level=logging.DEBUG)

    Command.from_args(parsed).run()
