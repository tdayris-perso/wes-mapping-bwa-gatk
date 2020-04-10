"""
This rule applies modifications in
the @RG, @SM, ... tags within bam file.
"""
rule picard_add_or_replace_group:
    input:
        "samtools/filtered/{sample}.bam"
    output:
        temp("picard/groups/{sample}.bam")
    message:
        "Replacing groups within {wildcards.sample} with Picard"
    threads:
        1
    version:
        swv
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 2048, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 60, 120)
        )
    log:
        "logs/picard/groups/{sample}.log"
    params:
        config["params"].get("picard_group_extra", "")
    wrapper:
        f"{swv}/bio/picard/addorreplacereadgroups"


"""
This rule marks duplicates in bam file
"""
rule picard_mark_duplicates:
    input:
        "picard/groups/{sample}.bam"
    output:
        bam = temp("picard/deduplicated/{sample}.bam"),
        metrics = "picard/stats/duplicates/{sample}.metrics.txt"
    message:
        "Dealing with duplicates in {wildcards.sample} with Picard"
    threads:
        1
    version:
        swv
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 2048, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 45 + 60, 240)
        )
    log:
        "logs/picard/duplicates/{sample}.log"
    params:
        config["params"].get("picard_dedup_extra", "")
    wrapper:
        f"{swv}/bio/picard/markduplicates"


"""
This rule collect metrics on aligned reads with picard tools.
"""
rule picard_alignment_summary:
    input:
        bam = "gatk/recal/{sample}.bam",
        ref = refs_pack_dict["fasta"]
    output:
        report(
            "picard/stats/summary/{sample}_summary.txt",
            caption="../report/picard_summary.rst",
            category="Quality",
            subcategory="Picard"
        )
    message:
        "Collecting alignment metrics from {wildcards.sample} with picard"
    threads:
        1
    version:
        swv
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 1024, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 60, 180)
        )
    log:
        "logs/picard/stats/{sample}.summary.log"
    params:
        config["params"].get("picard_summary_extra", "")
    wrapper:
        f"{swv}/bio/picard/collectalignmentsummarymetrics"


"""
This rule collect metrics on insert size of paired end reads with picard tools.
"""
rule picard_insert_size:
    input:
        "gatk/recal/{sample}.bam"
    output:
        txt = "picard/stats/size/{sample}.isize.txt",
        pdf = report(
            "picard/stats/size/{sample}.isize.pdf",
            caption="../report/picard_isize.rst",
            category="Quality",
            subcategory="Picard"
        )
    message:
        "Collecting insert size information on {wildcards.sample} with Picard."
    threads:
        1
    version:
        swv
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 1024, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 45 + 60, 180)
        )
    log:
        "logs/picard/stats/{sample}.isize.log"
    params:
        config["params"].get("picard_isize_extra", "")
    wrapper:
        f"{swv}/bio/picard/collectinsertsizemetrics"


"""
This rule re-builds fasta dictionnaries to avoid version issue
"""
rule picard_create_sequence_dictionnary:
    input:
        get_fasta_path()
    output:
        get_sequence_dict_path()
    message:
        "Building sequence dictionnary for reference fasta"
    log:
        "logs/picard/create_sequence_dictionnary/fasta.log"
    threads:
        1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 1024, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 45 + 60, 180)
        )
    params:
        extra = config["params"].get("picard_sequence_dict_extra", "")
    version:
        swv
    wrapper:
        f"{swv}/bio/picard/createsequencedictionary"
