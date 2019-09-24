### Variables ###
# Pytest
PYTEST       = pytest
PYFLAGS      = -v
TEST_CONFIG  = ../scripts/prepare_config.py
TEST_DESIGN  = ../scripts/prepare_design.py

# Conda
CONDA      = conda env create
CONDAFLAGS = --force
ENV_YAML   = ../envs/workflow.yaml

# Bash
BASH          = bash
BASHFLAG      =
TEST_PIPELINE = test.sh

default: all.unit.tests

### Unit Tests ###
# Running all tests
config.tests:
	$(PYTEST) $(PYFLAGS) $(TEST_CONFIG)

design.tests:
	$(PYTEST) $(PYFLAGS) $(TEST_DESIGN)

all.unit.tests:
	$(PYTEST) $(PYFLAGS) $(TEST_DESIGN) $(TEST_CONFIG)


### Continuous Integration Tests ###
# Environment building through conda
conda-tests:
	$(CONDA) --file $(ENV_YAML) $(CONDAFLAGS)

# Running snakemake on test datasets
ci-tests:
	$(BASH) $(BASHFLAG) $(TEST_PIPELINE)

clean:
	rm -rf .snakemake gatk/ bwa/ genome/ logs/ qc/ raw_data/ samtools/ tmp/ tmp_a_U/ TMP_BQSR_a_U/ report.html design.tsv config.yaml
