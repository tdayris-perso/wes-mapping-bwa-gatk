#!/bin/bash
set -euo pipefail

source .circleci/common.sh

if type conda > /dev/null; then exit 0; fi
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p miniconda
conda config --add channels defaults
conda config --add channels conda-forge
conda config --add channels bioconda
conda env create --file envs/workflows.yaml
