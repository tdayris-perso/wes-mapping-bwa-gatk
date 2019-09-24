#!/bin/bash

set -e

python3.7 ../scripts/prepare_design.py --single --recursive ${PWD} --debug

python3.7 ../scripts/prepare_config.py genomes/genome.fasta genomes/dbsnp.vcf.gz --debug --cold-storage /mnt

snakemake -s ../Snakefile --use-conda -j 4 --force

snakemake -s ../Snakefile --use-conda --report -j 4 --force
