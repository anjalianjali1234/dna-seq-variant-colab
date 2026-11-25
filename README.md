# DNA-Seq (Variant Analysis) Workshop · Google Colab edition

**Xenoi Biotech** · 30 days · 6 modules · online, self-paced with mentor guidance · 1–2 hours per day

Take real human sequencing reads all the way to a prioritised, annotated variant list, entirely in your web browser. No installation, no Linux machine and no prior programming are needed: every module is a Google Colab notebook.

**Workshop question:** can different variant callers recover the same small DNA changes in a real human sample (HG001 / NA12878), and how do we know which calls to trust? Every result is checked against the NIST Genome in a Bottle truth set.

## Modules

| Module | Days | Notebook | You will |
|---|---|---|---|
| 1 · Foundations | 1–5 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anjalianjali1234/dna-seq-variant-colab/blob/main/notebooks/M1_Foundations.ipynb) | Learn Linux basics, compare WGS/exome/panel designs, read FASTQ/BAM/VCF, run read QC (fastp) |
| 2 · Alignment | 6–10 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anjalianjali1234/dna-seq-variant-colab/blob/main/notebooks/M2_Alignment.ipynb) | Index the reference, map with BWA-MEM2, mark duplicates (Picard), plan BQSR (GATK), measure coverage |
| 3 · Variant calling | 11–15 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anjalianjali1234/dna-seq-variant-colab/blob/main/notebooks/M3_Variant_calling.ipynb) | Call SNPs and indels with GATK HaplotypeCaller, BCFtools and FreeBayes; gVCF workflow; hard filters; compare callers |
| 4 · Annotation | 16–20 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anjalianjali1234/dna-seq-variant-colab/blob/main/notebooks/M4_Annotation.ipynb) | Predict effects with Ensembl VEP, add gnomAD frequencies, check ClinVar, build an annotated table |
| 5 · Filtering & prioritization | 21–25 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anjalianjali1234/dna-seq-variant-colab/blob/main/notebooks/M5_Filtering_and_prioritization.ipynb) | Filter to a shortlist, apply inheritance and case-control logic, rank candidates, review in IGV |
| 6 · Mini-project & report | 26–30 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anjalianjali1234/dna-seq-variant-colab/blob/main/notebooks/M6_Mini_project_and_report.ipynb) | Run a filter-threshold benchmark, make figures, write a short scientific report |

## How it works

1. Click a **Open in Colab** badge and sign in with a Google account.
2. Run the **Session setup** cell first. It installs the tools (micromamba, bioconda) and downloads the checksum-verified data in about 3–5 minutes.
3. Modules 2–6 have a **catch-up** cell that rebuilds earlier outputs, because Colab starts fresh each session. Optionally save `run/` to Google Drive.
4. Work through each day: read, run, then answer the ✍️ exercises in your lab notebook.

## Data

Public HG001 (NA12878) reads from a 10 kb region of chromosome 20 (GRCh37: 10,000,001–10,010,000), a training reference, and the NIST truth VCF and confident-region BED, as distributed with Google's DeepVariant quick-start test data ([data/sources.tsv](data/sources.tsv)). The small region keeps every step fast; the limits this places on conclusions are discussed in the notebooks.

## Tools

fastp · BWA-MEM2 · SAMtools · Picard · GATK 4 (HaplotypeCaller, gVCF, VariantFiltration, BQSR) · BCFtools · FreeBayes · Ensembl VEP (live GRCh37 API, with an offline snapshot) · IGV (embedded with igv-notebook) · pandas and matplotlib. DeepVariant and ANNOVAR are covered as discussion and optional exercises, because Colab cannot run Docker and ANNOVAR requires registration.

## Repository layout

```
notebooks/   six module notebooks (open in Colab)
setup/       colab_setup.sh (tools + data), catchup.sh (rebuild earlier modules)
scripts/     call_variants.sh, benchmark.py, annotate.py
data/        download manifest and frozen VEP snapshot
```

## Certificate

Participants who submit the Module 6 report receive a Certificate of Completion from Xenoi Biotech Pvt. Ltd.; the capstone is independently evaluated.

---
Original workshop material © Xenoi Biotech Pvt. Ltd. All rights reserved. Public datasets, database annotations and software retain their respective licences.
