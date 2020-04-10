"""
This rule runs MultiQC in order to collect metrics on most of our tools and
raw files: Fastq + BWA + Samtools. We need to include the fasta reference for
the report option only.
More information at:
https://snakemake-wrappers.readthedocs.io/en/stable/wrappers/multiqc.html
"""
rule multiqc:
    input:
        **get_targets(no_multiqc=True)
    output:
        report(
            "qc/multiqc_report.html",
            caption="../report/multiqc.rst",
            category="Quality",
            subcategory="Complete"
        )
    params: ""
    threads: 1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048, 4096)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 10, 60)
        )
    version: "1.0"
    log:
        "logs/multiqc.log"
    message:
        "Gathering quality reports with MultiQC"
    wrapper:
        f"{swv}/bio/multiqc"
