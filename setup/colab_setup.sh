#!/usr/bin/env bash
# One-time setup for each Google Colab session (Colab resets when the runtime stops).
# Installs micromamba and the workshop tools into /content/env, then downloads the
# checksum-verified workshop data into run/input/. Takes about 3-5 minutes.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -x /content/env/bin/samtools ]; then
    echo ">>> Installing micromamba"
    mkdir -p /content/mamba
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C /content/mamba bin/micromamba
    echo ">>> Installing bioinformatics tools (this is the slow step)"
    /content/mamba/bin/micromamba create -y -q -p /content/env -c conda-forge -c bioconda \
        python=3.11 openjdk=17 fastp=0.24.1 bwa-mem2=2.2.1 samtools=1.22 bcftools=1.22 \
        picard=3.3 gatk4=4.6 freebayes=1.3.9 pandas matplotlib
else
    echo ">>> Tools already installed"
fi

echo ">>> Downloading workshop data (skipped if already present)"
mkdir -p run/input
while read -r file md5 url; do
    dest="run/input/$file"
    if ! echo "$md5  $dest" | md5sum --check --status 2>/dev/null; then
        curl --fail --location --retry 3 -s "$url" -o "$dest.part"
        echo "$md5  $dest.part" | md5sum --check --quiet
        mv "$dest.part" "$dest"
    fi
done < <(tail -n +2 data/sources.tsv)
[ -s run/input/ref.fa ] || gzip -dc run/input/ref.fa.gz > run/input/ref.fa
echo ">>> Setup complete"
