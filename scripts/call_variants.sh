#!/usr/bin/env bash
# Module 3: call SNVs/indels with three callers and normalise everything against one reference.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p run/calls
ref=run/input/ref.fa
bam=run/align/HG001.bam
region=chr20:10000001-10010000
printf 'chr20\t10000000\t10010000\n' > run/calls/target.bed

# 1. GATK HaplotypeCaller (local haplotype assembly)
gatk --java-options "-Xmx4g" HaplotypeCaller -R "$ref" -I "$bam" -L "$region" \
    -O run/calls/gatk.raw.vcf.gz --verbosity ERROR 2>/dev/null
# 2. BCFtools (pileup genotype likelihoods)
bcftools mpileup -Ou -r "$region" -q 20 -Q 20 -a FORMAT/DP,FORMAT/AD -f "$ref" "$bam" 2>/dev/null |
    bcftools call -mv -Oz -o run/calls/bcftools.raw.vcf.gz
# 3. FreeBayes (haplotype-based Bayesian caller)
freebayes -f "$ref" -t run/calls/target.bed -m 20 -q 20 "$bam" | bgzip > run/calls/freebayes.raw.vcf.gz

# Normalise (left-align, split multi-allelics) so callers can be compared allele by allele.
for name in gatk bcftools freebayes; do
    bcftools norm -f "$ref" -m -any "run/calls/$name.raw.vcf.gz" -Ou 2>/dev/null |
        bcftools sort -Oz -o "run/calls/$name.norm.vcf.gz" 2>/dev/null
    bcftools index -ft "run/calls/$name.norm.vcf.gz"
done
bcftools norm -f "$ref" -m -any run/input/truth.vcf.gz -Ou 2>/dev/null |
    bcftools view -i 'GT="alt"' -Ou | bcftools sort -Oz -o run/calls/truth.norm.vcf.gz 2>/dev/null
bcftools index -ft run/calls/truth.norm.vcf.gz
echo "Calls written to run/calls/"
