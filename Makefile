SHELL := bash
.ONESHELL:
.SHELLFLAGS := -euio pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

### Variables ###
# Tools
PYTEST         = pytest
BASH           = bash
CONDA          = conda
PYTHON         = python3.7
SNAKEMAKE      = snakemake
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

# Paths
TEST_CONFIG    = scripts/prepare_config.py
TEST_DESIGN    = scripts/prepare_design.py
SNAKE_FILE     = Snakefile
ENV_YAML       = envs/workflows.yaml
GENOME_PATH    = genomes/genome.fasta
DBSNP_PATH     = genomes/dbsnp.vcf.gz
READS_PATH     = reads/

# Arguments
ENV_NAME       = wes-mapping-bwa-gatk
SNAKE_THREADS  = 1

# Recipes
default: all-unit-tests

### UNIT TESTS ###
# Running all unit-tests (one for each python scripts)
all-unit-tests:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTEST} -v ${TEST_CONFIG} ${TEST_DESIGN}

# Running all unit test (on prepare_config.py only)
config-tests:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTEST} -v ${TEST_CONFIG} && \
	${PYTHON} ${TEST_CONFIG} ${GENOME_PATH} ${DBSNP_PATH} --debug --cold-storage /mnt

# Running all unit test (on prepare_design.py only)
design-tests:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTEST} -v ${TEST_DESIGN} && \
	${PYTHON} ${TEST_DESIGN} --single --recursive ${PWD} --debug

### Continuous Integration Tests ###
# Running snakemake on test datasets
ci-tests:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTHON} ${TEST_DESIGN} --single --recursive ${PWD} --output ${PWD}/tests/design.tsv --debug && \
	${PYTHON} ${TEST_CONFIG} ${GENOME_PATH} ${DBSNP_PATH} --workdir ${PWD}/tests/ --debug --cold-storage /mnt --samtools-sort-memory 1 && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --forceall --configfile ${PWD}/tests/config.yaml --directory ${PWD}/tests && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --report --directory ${PWD}/tests
.PHONY: ci-tests

# Running snakemake on test datasets with singularity flag raised on
singularity-tests:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${PYTHON} ${TEST_DESIGN} --single --recursive ${PWD} --output ${PWD}/tests/design.tsv --debug && \
	${PYTHON} ${TEST_CONFIG} ${GENOME_PATH} ${DBSNP_PATH} --workdir ${PWD}/tests/ --debug --cold-storage /mnt --samtools-sort-memory 1 && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --forceall --configfile ${PWD}/tests/config.yaml --use-singularity --directory ${PWD}/tests && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --report --directory ${PWD}/tests
.PHONY: singularity-tests

# Environment building through conda
conda-tests:
	${CONDA_ACTIVATE} base && \
	${CONDA} env create --file ${ENV_YAML} --force && \
	${CONDA} activate ${ENV_NAME}


# Cleaning Snakemake outputs
clean:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --force --configfile ${PWD}/tests/config.yaml --use-singularity --directory ${PWD}/tests --delete-all-output
.PHONY: clean


# Display pipeline graph
workflow.png:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --force --configfile ${PWD}/tests/config.yaml --directory ${PWD}/tests --rulegraph | dot -T png > workflow.png

example.png:
	${CONDA_ACTIVATE} ${ENV_NAME} && \
	${SNAKEMAKE} -s ${SNAKE_FILE} --use-conda -j ${SNAKE_THREADS} --force --configfile ${PWD}/tests/config.yaml --directory ${PWD}/tests --dag | dot -T png > example.png
