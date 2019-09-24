Material and Methods:
#####################

Quality control were made on raw `FastQ <https://en.wikipedia.org/wiki/FASTQ_format>`_ files with FastQC.

Raw reads are mapped by `BWA <https://github.com/lh3/bwa>`_ (1). Sort and conversion from unsorted SAM format into coordinate soerted BAM file is being done with `Picard <https://broadinstitute.github.io/picard/>`_ (2). possible mating errors are fixed with `Samtools <https://github.com/samtools/samtools>`_ (3), mapping is filtered with this very same tool. Groups are set with Picard alongside with duplicate removal. NM, MD and UQ tags are recalculated with `GATK <https://gatkforums.broadinstitute.org/gatk>`_ (4) due to possible errors introduced with previous fixmate operation. Finally, GATK performs base score recalibration on corrected reads.

Optional quality metrics are given with Picard, and merged with `MultiQC <https://multiqc.info/>`_ (5), with the initial quality controls performed in first hand.

This whole pipeline follows best practice for variant calling and allelic expression analysis (6, 7).

Optional arguments for the following steps are lister below:

- Genome indexation step: `{{snakemake.config.params.samtools_faidx_extra}}`
- Genome sequence dictionnary: `{{snakemake.config.params.picard_sequence_dict_extra}}`
- BWA genome indexation step: `{{snakemake.config.params.bwa_index_extra}}`
- BWA read mapping step: `{{snakemake.config.params.bwa_map_extra}}`
- Sam file into bam file sorting and conversion: `{{snakemake.config.params.picard_sort_sam_extra}}`
- Mate fiwing options: `{{snakemake.config.params.samtools_fixmate_extra}}`
- Filtering options: `{{snakemake.config.params.samtools_view}}`
- Read grouping options: `{{snakemake.config.params.picard_group_extra}}`
- Deduplication options: `{{snakemake.config.params.picard_dedup_extra}}`
- Base score recalibration options: `{{snakemake.config.params.gatk_bqsr_extra}}`
- Statistics over final mapping files: `{{snakemake.config.params.picard_summary_extra}}`
- Insert size estimation: `{{snakemake.config.params.picard_isize_extra}}`

Citations:

* 1. Li, Heng. "Aligning sequence reads, clone sequences and assembly contigs with BWA-MEM." arXiv preprint arXiv:1303.3997 (2013).
* 2. See GATK in point 4
* 3. Li, Heng, et al. "The sequence alignment/map format and SAMtools." Bioinformatics 25.16 (2009): 2078-2079.
* 4. McKenna, Aaron, et al. "The Genome Analysis Toolkit: a MapReduce framework for analyzing next-generation DNA sequencing data." Genome research 20.9 (2010): 1297-1303.
* 5. Ewels, Philip, et al. "MultiQC: summarize analysis results for multiple tools and samples in a single report." Bioinformatics 32.19 (2016): 3047-3048.
* 6. DePristo, Mark A., et al. "A framework for variation discovery and genotyping using next-generation DNA sequencing data." Nature genetics 43.5 (2011): 491.
* 7. Van der Auwera, Geraldine A., et al. "From FastQ data to high‐confidence variant calls: the genome analysis toolkit best practices pipeline." Current protocols in bioinformatics 43.1 (2013): 11-10.
