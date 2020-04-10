#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

"""
This script aims to prepare the configuration file used
by the wes-mapping-bwa-gatk pipeline

It goes through the arguments passed in command line and
builds a yaml formatted text file used as a configuration
file for the snakemake pipeline.

You can test this script with:
pytest -v ./prepare_config.py

Usage example:
# Whole pipeline
python3.7 /path/to/fasta_file.fa

# No quality controls, only quantification
python3.7 /path/to/fasta_file.fa --no-fastqc --no-multiqc

# Whole pipeline, verbose mode activated
python3.7 /path/to/fasta_file.fa -v
"""


import argparse             # Parse command line
import logging              # Traces and loggings
import logging.handlers     # Logging behaviour
import os                   # OS related activities
import pytest               # Unit testing
import shlex                # Lexical analysis
import sys                  # System related methods
import yaml                 # Parse Yaml files

from pathlib import Path             # Paths related methods
from typing import Dict, Any         # Typing hints


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


# Argument parsing functions
def parse_args(args: Any = sys.argv[1:]) -> argparse.ArgumentParser:
    """
    This function builds an object object to parse command line arguments

    Parameters
        args     Any             All command line arguments

    Return
                ArgumentParser   A object designed to parse the command line

    Example:
    >>> parse_args(shlex.split("/path/to/fasta.fa /path/to/known.vcf"))
    Namespace(bwa_index_extra='', bwa_map_extra='-T 20 -M',
    cold_storage='None', copy_extra='--verbose', debug=False,
    design='design.tsv', fasta='/path/to/fasta.fa',
    gatk_bqsr_extra='--verbosity DEBUG', known_vcf=['/path/to/known.vcf'],
    no_quality_control=False, picard_dedup_extra='REMOVE_DUPLICATES=true',
    picard_group_extra='RGLB=standard RGPL=illumina RGPU={sample}
    RGSM={sample}', picard_isize_extra='METRIC_ACCUMULATION_LEVEL=SAMPLE',
    picard_sequence_dict_extra='GENOME_ASSEMBLY=GRCH38 SPECIES=HSA
     URI=https://www.gencodegenes.org/human/', picard_sort_sam_extra='',
    picard_summary_extra='', quiet=False, samtools_faidx_extra='',
    samtools_fixmate_extra='-c -m', samtools_view='-b -h -F 12',
    singularity='docker://continuumio/miniconda3:4.4.10', threads=1,
    workdir='.')
    """
    main_parser = argparse.ArgumentParser(
        description="ok",  # sys.modules[__name__].doc,
        formatter_class=CustomFormatter,
        epilog="This script does not make any magic. Please check the prepared"
               " configuration file!"
    )

    # Positional arguments
    main_parser.add_argument(
        "fasta",
        help="Path to the genome sequence file file",
        type=str
    )

    main_parser.add_argument(
        "known_vcf",
        help="Space separated list of paths to known vcf files",
        type=str,
        nargs="+"
    )

    # Optional arguments
    main_parser.add_argument(
        "-d", "--design",
        help="Path to the design file (default: %(default)s)",
        type=str,
        default="design.tsv"
    )

    main_parser.add_argument(
        "-w", "--workdir",
        help="Path to raw data directory (default: %(default)s)",
        type=str,
        default="."
    )

    main_parser.add_argument(
        "-t", "--threads",
        help="Maximum number of threads used (default: %(default)s)",
        type=int,
        default=1
    )

    main_parser.add_argument(
        "-s", "--singularity",
        help="Name of the docker/singularity image (default: %(default)s)",
        type=str,
        default="docker://continuumio/miniconda3:4.4.10"
    )

    main_parser.add_argument(
        "--cold-storage",
        help="Path to cold storage mount points (default: %(default)s)",
        type=str,
        default="None",
        nargs="+"
    )

    main_parser.add_argument(
        "--no-quality-control",
        help="Do not perform any additional quality controls",
        action="store_true"
    )

    main_parser.add_argument(
        "--copy-extra",
        help="Extra parameters for bash copy (default: %(default)s)",
        type=str,
        default="--verbose"
    )

    main_parser.add_argument(
        "--bwa-index-extra",
        help="Extra parameters for bwa index (default: %(default)s)",
        type=str,
        default=""
    )

    main_parser.add_argument(
        "--bwa-map-extra",
        help="Extra parameters for bwa mem (default: %(default)s)",
        type=str,
        default="-T 20 -M"
    )

    main_parser.add_argument(
        "--picard-sort-sam-extra",
        help="Extra parameters for picard sort sam (default: %(default)s)",
        type=str,
        default=""
    )

    main_parser.add_argument(
        "--picard-group-extra",
        help="Extra parameters for picard read groups (default: %(default)s)",
        type=str,
        default="RGLB=standard RGPL=illumina RGPU={sample} RGSM={sample}"
    )

    main_parser.add_argument(
        "--picard-sequence-dict-extra",
        help="Extra parameters for picard create sequence dictionnary"
             " (default %(default)s)",
        type=str,
        default="GENOME_ASSEMBLY=GRCH38 SPECIES=HSA "
                "URI=https://www.gencodegenes.org/human/"
    )

    main_parser.add_argument(
        "--samtools-fixmate-extra",
        help="Extra parameters for samtools fixmate (default: %(default)s)",
        type=str,
        default="-c -m"
    )

    main_parser.add_argument(
        "--samtools-faidx-extra",
        help="Extra parameters for samtools fasta indexation",
        type=str,
        default=""
    )

    main_parser.add_argument(
        "--picard-dedup-extra",
        help="Extra parameters for Picard deduplicate (default: %(default)s)",
        type=str,
        default="REMOVE_DUPLICATES=true"
    )

    main_parser.add_argument(
        "--picard-isize-extra",
        help="Extra parameters for Picard insert "
             "size stats (default: %(default)s)",
        type=str,
        default="METRIC_ACCUMULATION_LEVEL=SAMPLE"
    )

    main_parser.add_argument(
        "--gatk-bqsr-extra",
        help="Extra parameters for GATK BQSR (default: %(default)s)",
        type=str,
        default="--verbosity DEBUG"
    )

    main_parser.add_argument(
        "--picard-summary-extra",
        help="Extra parameters for Picard summary"
             "(default: %(default)s)",
        type=str,
        default=""
    )

    main_parser.add_argument(
        "--samtools-view",
        help="Extra parameters for Picard summary"
             "(default: %(default)s)",
        type=str,
        default="-b -h -F 12"
    )

    main_parser.add_argument(
        "--samtools-sort-memory",
        help="Amount of memory allocated for samtools sort "
             "(default: %(default)s G)",
        type=str,
        default="8"
    )

    # Logging options
    log = main_parser.add_mutually_exclusive_group()
    log.add_argument(
        "--debug",
        help="Set logging in debug mode",
        default=False,
        action='store_true'
    )

    log.add_argument(
        "--quiet",
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
    options = parse_args(shlex.split("/path/to/fasta.fa /path/to/known.vcf"))

    expected = argparse.Namespace(
        bwa_index_extra='',
        bwa_map_extra='-T 20 -M',
        cold_storage='None',
        copy_extra='--verbose',
        debug=False,
        design='design.tsv',
        fasta='/path/to/fasta.fa',
        gatk_bqsr_extra='--verbosity DEBUG',
        known_vcf=['/path/to/known.vcf'],
        no_quality_control=False,
        picard_dedup_extra='REMOVE_DUPLICATES=true',
        picard_group_extra=(
            'RGLB=standard RGPL=illumina '
            'RGPU={sample} RGSM={sample}'
        ),
        picard_isize_extra='METRIC_ACCUMULATION_LEVEL=SAMPLE',
        picard_sequence_dict_extra=(
            'GENOME_ASSEMBLY=GRCH38 SPECIES=HSA '
            'URI=https://www.gencodegenes.org/human/'
        ),
        picard_sort_sam_extra='',
        picard_summary_extra='',
        quiet=False,
        samtools_faidx_extra='',
        samtools_fixmate_extra='-c -m',
        samtools_view='-b -h -F 12',
        samtools_sort_memory="8",
        singularity='docker://continuumio/miniconda3:4.4.10',
        threads=1,
        workdir='.'
    )
    assert options == expected


# Building yaml formatted arguments
def args_to_dict(args: argparse.ArgumentParser) -> Dict[str, Any]:
    """
    Parse command line arguments and return a dictionnary ready to be
    dumped into yaml

    Parameters:
        args        ArgumentParser      Parsed arguments from command line

    Return:
                    Dict[str, Any]      A dictionnary containing the parameters
                                        for the pipeline

    Example:
    >>> args_to_dict(
        parse_args(shlex.split("/path/to/fasta.fa /path/to/known.vcf"))
    )
    {'cold_storage': 'None',
     'design': 'design.tsv',
     'params': {'bwa_index_extra': '',
      'bwa_map_extra': '-T 20 -M',
      'copy_extra': '--verbose',
      'gatk_bqsr_extra': '--verbosity DEBUG',
      'picard_dedup_extra': 'REMOVE_DUPLICATES=true',
      'picard_group_extra': 'RGLB=standard RGPL=illumina RGPU={sample}
       RGSM={sample}',
      'picard_isize_extra': 'METRIC_ACCUMULATION_LEVEL=SAMPLE',
      'picard_sequence_dict_extra': 'GENOME_ASSEMBLY=GRCH38 SPECIES=HSA
       URI=https://www.gencodegenes.org/human/',
      'picard_sort_sam_extra': '',
      'picard_summary_extra': '',
      'samtools_faidx_extra': '',
      'samtools_fixmate_extra': '-c -m',
      'samtools_view': '-b -h -F 12'},
     'ref': {'fasta': '/path/to/fasta.fa', 'known': ['/path/to/known.vcf']},
     'singularity_docker_image': 'docker://continuumio/miniconda3:4.4.10',
     'threads': 1,
     'workdir': '.',
     'workflow': {'fastqc': True, 'mapping_quality': True, 'multiqc': True}}
    """
    return {
        "design": args.design,
        "workdir": args.workdir,
        "threads": args.threads,
        "singularity_docker_image": args.singularity,
        "cold_storage": args.cold_storage,
        "ref": {
            "fasta": args.fasta,
            "known": args.known_vcf
        },
        "workflow": {
            "fastqc": not args.no_quality_control,
            "multiqc": not args.no_quality_control,
            "mapping_quality": not args.no_quality_control,
        },
        "params": {
            "copy_extra": args.copy_extra,
            "bwa_index_extra": args.bwa_index_extra,
            "bwa_map_extra": args.bwa_map_extra,
            "picard_sort_sam_extra": args.picard_sort_sam_extra,
            "picard_group_extra": args.picard_group_extra,
            "picard_dedup_extra": args.picard_dedup_extra,
            "picard_isize_extra": args.picard_isize_extra,
            "gatk_bqsr_extra": args.gatk_bqsr_extra,
            "picard_summary_extra": args.picard_summary_extra,
            "samtools_fixmate_extra": args.samtools_fixmate_extra,
            "picard_sequence_dict_extra": args.picard_sequence_dict_extra,
            "samtools_view": args.samtools_view,
            "samtools_faidx_extra": args.samtools_faidx_extra,
            "samtools_sort_memory": args.samtools_sort_memory
        }
    }


def test_args_to_dict() -> None:
    """
    This function simply tests the args_to_dict function with expected output

    Example:
    >>> pytest -v prepare_config.py -k test_args_to_dict
    """
    expected = {
        'cold_storage': 'None',
        'design': 'design.tsv',
        'params': {
            'bwa_index_extra': '',
            'bwa_map_extra': '-T 20 -M',
            'copy_extra': '--verbose',
            'gatk_bqsr_extra': '--verbosity DEBUG',
            'picard_dedup_extra': 'REMOVE_DUPLICATES=true',
            'picard_group_extra': ('RGLB=standard RGPL=illumina '
                                   'RGPU={sample} RGSM={sample}'),
            'picard_isize_extra': 'METRIC_ACCUMULATION_LEVEL=SAMPLE',
            'picard_sequence_dict_extra': (
                'GENOME_ASSEMBLY=GRCH38 SPECIES=HSA'
                ' URI=https://www.gencodegenes.org/human/'
            ),
            'picard_sort_sam_extra': '',
            'picard_summary_extra': '',
            'samtools_faidx_extra': '',
            'samtools_fixmate_extra': '-c -m',
            'samtools_view': '-b -h -F 12',
            "samtools_sort_memory": '8'
        },
        'ref': {'fasta': '/path/to/fasta.fa', 'known': ['/path/to/known.vcf']},
        'singularity_docker_image': 'docker://continuumio/miniconda3:4.4.10',
        'threads': 1,
        'workdir': '.',
        'workflow': {'fastqc': True, 'mapping_quality': True, 'multiqc': True}
    }
    test = args_to_dict(
        parse_args(shlex.split("/path/to/fasta.fa /path/to/known.vcf"))
    )

    assert test == expected


# Yaml formatting
def dict_to_yaml(indict: Dict[str, Any]) -> str:
    """
    This function makes the dictionnary to yaml formatted text

    Parameters:
        indict  Dict[str, Any]  The dictionnary containing the pipeline
                                parameters, extracted from command line

    Return:
                str             The yaml formatted string, directly built
                                from the input dictionnary

    Examples:
    >>> import yaml
    >>> example_dict = {
        "bar": "bar-value",
        "foo": ["foo-list-1", "foo-list-2"]
    }
    >>> dict_to_yaml(example_dict)
    'bar: bar-value\nfoo:\n- foo-list-1\n- foo-list-2\n'
    >>> print(dict_to_yaml(example_dict))
    bar: bar-value
    foo:
    - foo-list-1
    - foo-list-2
    """
    return yaml.dump(indict, default_flow_style=False)


def test_dict_to_yaml() -> None:
    """
    This function tests the dict_to_yaml function with pytest

    Example:
    >>> pytest -v prepare_config.py -k test_dict_to_yaml
    """
    expected = 'bar: bar-value\nfoo:\n- foo-list-1\n- foo-list-2\n'
    example_dict = {
        "bar": "bar-value",
        "foo": ["foo-list-1", "foo-list-2"]
    }
    assert dict_to_yaml(example_dict) == expected


# Core of this script
def main(args: argparse.ArgumentParser) -> None:
    """
    This function performs the whole configuration sequence

    Parameters:
        args    ArgumentParser      The parsed command line

    Example:
    >>> main(parse_args(shlex.split("/path/to/fasta")))
    """
    # Building pipeline arguments
    logger.debug("Building configuration file:")
    config_params = args_to_dict(args)
    output_path = Path(args.workdir) / "config.yaml"

    # Saving as yaml
    with output_path.open("w") as config_yaml:
        logger.debug(f"Saving results to {str(output_path)}")
        config_yaml.write(dict_to_yaml(config_params))


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args)

    try:
        logger.debug("Preparing configuration")
        main(args)
    except Exception as e:
        logger.exception("%s", e)
        sys.exit(1)
    sys.exit(0)
