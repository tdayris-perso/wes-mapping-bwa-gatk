#!/usr/bin/python3.7
# -*- coding: utf-8 -*-

"""
This script aims to prepare the list of files to be processed
by the wes-mapping-bwa-gatk pipeline

It iterates over a given directory, lists all fastq files. As a pair of
fastq files usually have names that follows each other in the alphabetical
order, this script sorts the fastq files names and, by default, creates
pairs of fastq files that way.

Finally, it writes these pairs, using the longest common substring as
identifier. The written file is a TSV file.

You can test this script with:
pytest -v ./prepare_design.py

Usage example:
# Single ended reads example:
python3.7 ./prepare_design.py ../tests/reads --single

# Paired-end libary example:
python3.7 ./prepare_design.py ../tests/reads

# Search in sub-directories:
python3.7 ./prepare_design.py ../tests --recursive
"""

import argparse           # Parse command line
import logging            # Traces and loggings
import logging.handlers   # Logging behaviour
import os                 # OS related activities
import pandas as pd       # Parse TSV files
import pytest             # Unit testing
import shlex              # Lexical analysis
import sys                # System related methods

from pathlib import Path                        # Paths related methods
from typing import Dict, Generator, List, Any   # Type hints

logger = logging.getLogger(
    os.path.splitext(os.path.basename(sys.argv[0]))[0]
)


# Building custom class for help formatter
class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    """
    This class is used only to allow line breaks in the documentation,
    without breaking the classic argument formatting.
    """
    pass


# Handling logging options
# No tests for this function
def setup_logging(args: argparse.ArgumentParser) -> None:
    """
    Configure logging behaviour
    """
    root = logging.getLogger("")
    root.setLevel(logging.WARNING)
    logger.setLevel(args.debug and logging.DEBUG or logging.INFO)
    if not args.quiet:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            "%(levelname)s [%(name)s]: %(message)s"
        ))
        root.addHandler(ch)


# Processing functions
# Looking for fastq files
def search_fq(fq_dir: Path,
              recursive: bool = False) -> Generator[str, str, None]:
    """
    Iterate over a directory and search for fastq files

    Parameters:
        fq_dir      Path        Path to the fastq directory in which to search
        recursive   bool        A boolean, weather to search recursively in
                                sub-directories (True) or not (False)

    Return:
                    Generator[str, str, None]       A Generator of paths

    Example:
    >>> search_fq(Path("../tests/reads/"))
    <generator object search_fq at 0xXXXXXXXXXXXX>

    >>> list(search_fq(Path("../tests/", True)))
    [PosixPath('../tests/reads/a_U.fastq')]
    """
    for path in fq_dir.iterdir():
        if path.is_dir():
            if recursive is True:
                yield from search_fq(path, recursive)
            else:
                continue

        if path.name.endswith((".fq", ".fq.gz", ".fastq", ".fastq.gz")):
            yield path


def test_search_fq():
    """
    This function tests the ability of the function "search_fq" to find the
    fastq files in the given directory

    Example:
    pytest -v prepare_design.py -k test_search_fq
    """
    path = Path("../tests/reads/")
    expected = [Path('../tests/reads/a_U.fastq')]
    assert sorted(list(search_fq(path))) == sorted(expected)


def parse_args(args: Any = sys.argv[1:]) -> argparse.ArgumentParser:
    """
    Build a command line parser object

    Parameters:
        args    Any                 Command line arguments

    Return:
                ArgumentParser      Parsed command line object

    Example:
    >>> parse_args(shlex.split("/path/to/fasta --single"))
    Namespace(output='design.tsv', path='/path/to/fastq/dir', recursive=False,
    single=False)
    """
    main_parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter,
        epilog="Each tool belong to their respective authors"
    )

    main_parser.add_argument(
        "path",
        help="Path to the directory containing fastq files",
        type=str
    )

    main_parser.add_argument(
        "-s", "--single",
        help="The samples are single ended rnaseq reads, not pair ended",
        action="store_true"
    )

    main_parser.add_argument(
        "-r", "--recursive",
        help="Recursively search in sub-directories for fastq files",
        action="store_true"
    )

    main_parser.add_argument(
        "-o", "--output",
        help="Path to output file (default: %(default)s)",
        type=str,
        default="design.tsv"
    )

    # Logging options
    log = main_parser.add_mutually_exclusive_group()
    log.add_argument(
        "-d", "--debug",
        help="Set logging in debug mode",
        default=False,
        action='store_true'
    )

    log.add_argument(
        "-q", "--quiet",
        help="Turn off logging behaviour",
        default=False,
        action='store_true'
    )

    return main_parser.parse_args(args)


def test_parse_args() -> None:
    """
    This function tests the command line parsing

    Example:
    >>> pytest -v prepare_config.py -k test_parse_args
    """
    options = parse_args(shlex.split("/path/to/fastq/dir/ --single"))
    expected = argparse.Namespace(
        output='design.tsv',
        path='/path/to/fastq/dir/',
        recursive=False,
        single=True,
        quiet=False,
        debug=False
    )
    assert options == expected


# Turning the FQ list into a dictionnary
def classify_fq(fq_files: List[Path], single: bool = True) -> Dict[str, Path]:
    """
    Return a dictionnary with identified fastq files (paried or not)

    Parameters:
        fq_files    List[Path]      A list of paths to iterate over
        paired      bool            A boolean, weather the dataset is
                                    pair-ended (True) or single-ended (False)

    Return:
                    Dict[str, Path] A dictionnary: for each Sample ID, the ID
                                    is repeated alongside with the upstream
                                    /downstream fastq files.

    Example:
    # Paired-end single sample
    >>> classify_fq([Path("file1.R1.fq"), Path("file1.R2.fq")], True)
    {'file1.R1.fq': {'Downstream_file': PosixPath("/path/to/file1.R1.fq"),
     'Sample_id': 'file1.R1',
     'Upstream_file': PosixPath('/path/to/file1.R2.fq')}

    # Single-ended single sample
    >>> classify_fq([Path("file1.fq")], False)
    {'file1.fq': {'Sample_id': 'file1',
     'Upstream_file': PosixPath('/path/to/file1.fq')}}
    """
    fq_dict = {}
    if single is True:
        logger.debug("Single-ended design")
        for fq in fq_files:
            fq_dict[fq.name] = {
                "Sample_id": fq.stem,
                "Upstream_file": fq.absolute()
            }
    else:
        logger.debug("Pair-ended design")
        for fq1, fq2 in zip(fq_files[0::2], fq_files[1::2]):
            fq_dict[fq1.name] = {
                "Sample_id": fq1.stem,
                "Upstream_file": fq1.absolute(),
                "Downstream_file": fq2.absolute()
            }

    return fq_dict


def test_classify_fq():
    """
    This function takes input from the pytest decorator
    to test the classify_fq function

    Example:
    pytest -v ./prepare_design.py -k test_classify_fq
    """
    prefix = Path(__file__).parent.parent
    classification = classify_fq([prefix / "file1.fq"], False)
    expected = {
        'file1.fq': {
            'Sample_id': 'file1',
            'Upstream_file': prefix / 'file1.fq'
        }
    }
    logger = logging.getLogger(
        os.path.splitext(os.path.basename(sys.argv[0]))[0]
    )
    assert classification == expected


def main(args: argparse.ArgumentParser) -> None:
    """
    This function performs the whole preparation sequence

    Parameters:
        args    ArgumentParser      The parsed command line

    Example:
    >>> main(parse_args(shlex.split("/path/to/fasta/dir/")))
    """
    fq_list = sorted(list(search_fq(Path(args.path), args.recursive)))
    logger.debug(fq_list)
    fq_dict = classify_fq(fq_list, args.single)
    logger.debug(fq_dict)

    data = pd.DataFrame(fq_dict).T
    logger.debug(data.head())
    data.to_csv(args.output, sep="\t", index=False)


if __name__ == '__main__':
    # Parsing command line
    args = parse_args()
    setup_logging(args)

    try:
        logger.debug("Preparing design")
        main(args)
    except Exception as e:
        logger.exception("%s", e)
        sys.exit(1)
    sys.exit(0)
