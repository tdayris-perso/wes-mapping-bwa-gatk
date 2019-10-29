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
GENOME_PATH    = tests/genomes/genome.fasta
DBSNP_PATH     = tests/genomes/dbsnp.vcf.gz
READS_PATH     = tests/reads/

# Arguments
ENV_NAME       = wes-mapping-bwa-gatk
SNAKE_THREADS  = 1

# Recipes
default: all-unit-tests

### UNIT TESTS ###
# Running all tests
all-unit-tests: SHELL:=$(BASH) -i
all-unit-tests:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	$(PYTEST) -v $(TEST_CONFIG) $(TEST_DESIGN)

# Running tests on configuration only
config-tests: SHELL:=$(BASH) -i
config-tests:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	$(PYTEST) -v $(TEST_CONFIG) && \
	$(PYTHON) $(TEST_CONFIG) $(GENOME_PATH) $(DBSNP_PATH) --debug --cold-storage /mnt

# Running tests on design only
design-tests: SHELL:=$(BASH) -i
design-tests:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	$(PYTEST) -v $(TEST_DESIGN) && \
	$(PYTHON) $(TEST_DESIGN) --single --recursive ${PWD} --debug

### Continuous Integration Tests ###
# Running snakemake on test datasets
ci-tests: SHELL:=$(BASH) -i
ci-tests:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	$(PYTHON) $(TEST_DESIGN) --single --recursive ${PWD} --debug && \
	$(PYTHON) $(TEST_CONFIG) $(GENOME_PATH) $(DBSNP_PATH) --debug --cold-storage /mnt --samtools-sort-memory 1 && \
	$(SNAKEMAKE) -s $(SNAKE_FILE) --use-conda -j $(SNAKE_THREADS) --force --configfile ${PWD}/config.yaml && \
	$(SNAKEMAKE) -s $(SNAKE_FILE) --use-conda -j $(SNAKE_THREADS) --report

# Environment building through conda
conda-tests: SHELL:=$(BASH) -i
conda-tests:
	$(CONDA_ACTIVATE) base && \
	$(CONDA) env create --file $(ENV_YAML) --force && \
	$(CONDA) activate $(ENV_NAME)
