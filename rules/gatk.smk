"""
This rule takes in a coordinate-sorted SAM or BAM and calculatesthe NM, MD,
and UQ tags by comparing with the reference. These tags may be broken by
previous corrections.
"""
rule gatk_SetNmMdAndUqTags:
    input:
        bam = "picard/deduplicated/{sample}.bam",
        ref = refs_pack_dict["fasta"],
        ref_index = refs_pack_dict["faidx"],
        ref_dict = refs_pack_dict["fadict"]
    output:
        bam = "gatk/setmnanduqtags/{sample}.bam"
    message:
        "Fixing possible broken MN, MD and UQ tags on {wildcards.sample}"
    threads:
        1
    version:
        "1.0"
    conda:
        "../envs/gatk.yaml"
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 7168, 16384)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 180, 480)
        )
    log:
        "logs/gatk/setmnanduqtags/{sample}.log"
    shell:
        "gatk SetNmMdAndUqTags --INPUT {input.bam} --OUTPUT {output.bam} "
        "--REFERENCE_SEQUENCE {input.ref} --TMP_DIR tmp_{wildcards.sample} "
        "> {log} 2>&1"


"""
This rule performs both BQSR table computation and its
application to the original input bam file
"""
rule gatk_bqsr:
    input:
        bam = "gatk/setmnanduqtags/{sample}.bam",
        bam_index = "gatk/setmnanduqtags/{sample}.bam.bai",
        ref = refs_pack_dict["fasta"],
        ref_index = refs_pack_dict["faidx"],
        ref_dict = refs_pack_dict["fadict"],
        known = refs_pack_dict["known_vcf"],
        known_index = refs_pack_dict["known_index"]
    output:
        bam = report(
            "gatk/recal/{sample}.bam",
            caption="../report/gatk.rst",
            category="Mapping"
        )
    message:
        "Recalibrating variants in {wildcards.sample} with GATK"
    threads:
        1
    version:
        swv
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 7168, 16384)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 180, 480)
        )
    # log:
    #     "logs/gatk/bqsr/{sample}.log"
    params:
        java_opts = (
            lambda wildcards, resources: get_java_args(wildcards, resources)
        ),
        extra = (
            lambda wildcards: get_gatk_args(wildcards)
        )
    wrapper:
        f"{swv}/bio/gatk/baserecalibrator"
