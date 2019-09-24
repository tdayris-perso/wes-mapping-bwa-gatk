"""
This rule uses BWA to index a fasta formatted genome sequence
"""
rule bwa_index:
    input:
        refs_pack_dict['fasta']
    output:
        expand(
            "bwa/index/{genome}.{ext}",
            genome=os.path.basename(refs_pack_dict["fasta"]),
            ext=["amb", "ann", "bwt", "pac"]
        )
    message:
        "Indexing {input} with BWA"
    threads:
        1
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 8192 + 2048, 20480)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 120, 480)
        )
    version: swv
    log:
        "logs/bwa/index.log"
    params:
        prefix = f"bwa/index/{os.path.basename(refs_pack_dict['fasta'])}"
    wrapper:
        f"{swv}/bio/bwa/index"


"""
This rule performs the actual bwa mem mapping
"""
rule bwa_mem:
    input:
        unpack(fq_pairs_w),
        index = expand(
            "bwa/index/{genome}.{ext}",
            genome=os.path.basename(refs_pack_dict["fasta"]),
            ext=["amb", "ann", "bwt", "pac"]
        )
    output:
        temp("bwa/mapping/{sample}.bam")
    message:
        "Mapping {wildcards.sample} with BWA mem"
    threads:
        min(config["threads"], 12)
    resources:
        mem_mb = (
            lambda wildcards, attempt: min(attempt * 8192 + 2048, 20480)
        ),
        time_min = (
            lambda wildcards, attempt: min(attempt * 120, 480)
        )
    version: swv
    params:
        index = f"bwa/index/{os.path.basename(refs_pack_dict['fasta'])}",
        extra = config['params'].get('bwa_map_extra', ""),
        sort = "picard",
        sort_order = "coordinate",
        sort_extra = config['params'].get('picard_sort_sam_extra', "")
    log:
        "logs/bwa_mem_{sample}.log"
    wrapper:
        f"{swv}/bio/bwa/mem"
