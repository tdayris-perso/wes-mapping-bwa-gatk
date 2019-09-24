"""
This rule sorts reads by name for fixmate
"""
rule samtools_sort_query:
    input:
        "bwa/mapping/{sample}.bam"
    output:
        temp("samtools/query_sort/{sample}.bam")
    message:
        "Sorting {wildcards.sample} reads by query name for fixing mates"
    threads:
        1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 8192 + 2048, 24576)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 75, 225)
        )
    log:
        "logs/samtools/query_sort_{sample}.log"
    params:
        f"-m {config['params'].get('samtools_sort_memory', '8')}G -n"
    wrapper:
        f"{swv}/bio/samtools/sort"


"""
This rule uses Samtools to perform fix mate operation on
BWA output. It does not use any wrapper since (1) it does
not exists, and (2) co-workers are currently writing the
wrapper
"""
rule samtools_fixmate:
    input:
        "samtools/query_sort/{sample}.bam"
    output:
        temp("samtools/fixmate/{sample}.bam")
    message:
        "Fixing mates in {wildcards.sample} BWA's output"
    threads:
        1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 2048, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 45, 180)
        )
    version:
        swv
    log:
        "logs/samtools/fixmate_{sample}.log"
    params:
        extra = config["params"].get("samtools_fixmate_extra", "")
    wrapper:
        f"{swv}/bio/samtools/fixmate"


"""
This rule sorts reads by position for further analyses
"""
rule samtools_sort_coordinate:
    input:
        "samtools/fixmate/{sample}.bam"
    output:
        temp("samtools/position_sort/{sample}.bam")
    message:
        "Sorting {wildcards.sample} reads by query name for fixing mates"
    threads:
        1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 8192 + 2048, 24576)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 75, 225)
        )
    version:
        swv
    log:
        "logs/samtools/query_sort_{sample}.log"
    params:
        f"-m {config['params'].get('samtools_sort_memory', '8')}G"
    wrapper:
        f"{swv}/bio/samtools/sort"


"""
This rule remove unmapped mates as GATK does not allow them
"""
rule samtools_filter_unmaped:
    input:
        "samtools/position_sort/{sample}.bam"
    output:
        temp("samtools/filtered/{sample}.bam")
    message:
        "Removing unmated reads in {wildcards.sample}"
    threads:
        1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 2048, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 45, 180)
        )
    version:
        swv
    log:
        "logs/samtools/filter_{sample}.log"
    params:
        config["params"].get("samtools_view", "")
    wrapper:
        f"{swv}/bio/samtools/view"


"""
This rule indexes bam files bafore BQSR
"""
rule samtools_index:
    input:
        "gatk/setmnanduqtags/{sample}.bam"
    output:
        "gatk/setmnanduqtags/{sample}.bam.bai"
    message:
        "Indexing {wildcards.sample} right before BQSR"
    threads:
        1
    params:
        ""
    version:
        swv
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 2048, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 45, 180)
        )
    log:
        "logs/samtools/index/setmnanduqtags_{sample}.log"
    wrapper:
        f"{swv}/bio/samtools/index"


"""
This rule build fasta indexes to avoid version issues
"""
rule samtools_faidx:
    input:
        "genome/{fasta}"
    output:
        "genome/{fasta}.fai"
    message:
        "Indexing the genome reference: {wildcards.fasta}"
    threads:
        1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 2048 + 2048, 8192)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 45, 180)
        )
    params:
        config["params"].get("samtools_faidx_extra", "")
    version:
        swv
    log:
        "logs/samtools/faidx/{fasta}.log"
    wrapper:
        f"{swv}/bio/samtools/faidx"
