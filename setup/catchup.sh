#!/usr/bin/env bash
# Rebuild the outputs of earlier modules in a fresh Colab session.
# Usage: bash setup/catchup.sh N   -> runs modules 1..N quietly (N = 1, 2 or 3)
set -euo pipefail
cd "$(dirname "$0")/.."
N=${1:-3}
ref=run/input/ref.fa
region=chr20:10000001-10010000

if [ "$N" -ge 1 ] && [ ! -s run/qc/R1.fq.gz ]; then
    echo ">>> Module 1: reads and QC"
    mkdir -p run/qc
    samtools collate -u -O run/input/reads.bam | samtools fastq -F 0x900 -n \
        -1 run/input/R1.fq.gz -2 run/input/R2.fq.gz -s run/input/orphans.fq.gz -0 /dev/null - 2>/dev/null
    fastp -i run/input/R1.fq.gz -I run/input/R2.fq.gz -o run/qc/R1.fq.gz -O run/qc/R2.fq.gz \
        --thread 2 --dont_eval_duplication --html run/qc/fastp.html --json run/qc/fastp.json 2>/dev/null
fi

if [ "$N" -ge 2 ] && [ ! -s run/align/HG001.bam ]; then
    echo ">>> Module 2: alignment"
    mkdir -p run/align
    samtools faidx "$ref"
    [ -s run/input/ref.dict ] || samtools dict "$ref" -o run/input/ref.dict
    [ -s "$ref.bwt.2bit.64" ] || bwa-mem2 index "$ref" 2>/dev/null
    bwa-mem2 mem -t 2 -R '@RG\tID:HG001.region\tSM:HG001\tPL:ILLUMINA\tLB:lib1' "$ref" \
        run/qc/R1.fq.gz run/qc/R2.fq.gz 2>/dev/null | samtools sort -o run/align/sorted.bam -
    picard MarkDuplicates -I run/align/sorted.bam -O run/align/HG001.bam \
        -M run/align/duplicates.txt --CREATE_INDEX false --VERBOSITY ERROR 2>/dev/null
    samtools index run/align/HG001.bam
    samtools depth -aa -r "$region" run/align/HG001.bam > run/align/depth.tsv
fi

if [ "$N" -ge 3 ] && [ ! -s run/calls/gatk.raw.vcf.gz ]; then
    echo ">>> Module 3: variant calling (GATK, BCFtools, FreeBayes)"
    bash scripts/call_variants.sh
fi
echo ">>> Catch-up complete"
