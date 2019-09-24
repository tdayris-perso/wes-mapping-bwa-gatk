"""
This rule indexes VCF files to avoid version issues
"""
rule vcf_index_tbi:
    input:
        "genome/{file}.vcf.gz"
    output:
        "genome/{file}.vcf.gz.tbi"
    threads:
        min(config["threads"], 6)
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 2048, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 45, 180)
        )
    version:
        1
    conda:
        "../envs/bcftools.yaml"
    log:
        "logs/bcftools/index/{file}.log"
    params:
        config["params"].get("bcftools_index", "")
    shell:
        "bcftools index --tbi --threads {threads} "
        "--force {input} --output-file {output} "
        "> {log} 2>&1"
