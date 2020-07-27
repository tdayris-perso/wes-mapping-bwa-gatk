import snakemake.utils  # Load snakemake API
import sys              # System related operations

# Python 3.7 is required
if sys.version_info < (3, 8):
    raise SystemError("Please use Python 3.8 or later.")

# Snakemake 5.14.0 at least is required
snakemake.utils.min_version("5.20.1")

include: "rules/common.smk"
include: "rules/copy.smk"
include: "rules/fastqc.smk"
include: "rules/multiqc.smk"
include: "rules/bwa.smk"
include: "rules/samtools.smk"
include: "rules/picard.smk"
include: "rules/gatk.smk"
include: "rules/htslib.smk"

workdir: config["workdir"]
singularity: config["singularity_docker_image"]
localrules: copy_fastq, copy_extra
ruleorder: copy_extra > samtools_faidx
ruleorder: copy_extra > picard_create_sequence_dictionnary

rule all:
    input:
        **targets_dict
    message:
        "Finishing the pipeline"
