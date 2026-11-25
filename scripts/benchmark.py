"""Compare normalised calls with the NIST/GIAB truth set inside the target and confident BED.

Usage: python scripts/benchmark.py [min_qual] [min_dp]   (defaults 30 and 10)
Writes run/report/benchmark_q{QUAL}_dp{DP}.tsv and run/report/alleles_q{QUAL}_dp{DP}.tsv
"""
import csv
import subprocess
import sys
from pathlib import Path

QUAL = float(sys.argv[1]) if len(sys.argv) > 1 else 30
DP = int(sys.argv[2]) if len(sys.argv) > 2 else 10
CALLERS = ["gatk", "bcftools", "freebayes"]
TSTART, TEND = 10000000, 10010000  # 0-based half-open target

def alleles(path, expr=None):
    cmd = ["bcftools", "view", "-Ou"]
    if expr:
        cmd += ["-i", expr]
    view = subprocess.run(cmd + [str(path)], capture_output=True, check=True).stdout
    text = subprocess.run(["bcftools", "query", "-f", "%CHROM\t%POS\t%REF\t%ALT\n", "-"],
                          input=view, capture_output=True, check=True).stdout.decode()
    return {(c, int(p), r, a) for c, p, r, a in (l.split("\t") for l in text.splitlines())}

beds = [l.split() for l in Path("run/input/confident.bed").read_text().splitlines() if l.strip()]

def inside(key):
    c, p, r, _ = key
    return any(c == bc and max(TSTART, int(s)) <= p - 1 and p - 1 + len(r) <= min(TEND, int(e)) for bc, s, e in beds)

calls = Path("run/calls")
out = Path("run/report"); out.mkdir(parents=True, exist_ok=True)
truth = set(filter(inside, alleles(calls / "truth.norm.vcf.gz")))
if not truth:
    sys.exit("No benchmark alleles in target: check build, contig names and BED.")
filt = f'GT="alt" && QUAL>={QUAL} && FORMAT/DP>={DP}'
sets = {n: alleles(calls / f"{n}.norm.vcf.gz", filt) for n in CALLERS}
tag = f"q{int(QUAL)}_dp{DP}"
with (out / f"benchmark_{tag}.tsv").open("w") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["caller", "min_qual", "min_dp", "TP", "FP", "FN", "precision", "recall"])
    for n, v in sets.items():
        q = set(filter(inside, v)); tp = len(q & truth)
        prec = round(tp / len(q), 4) if q else "undefined"
        w.writerow([n, QUAL, DP, tp, len(q - truth), len(truth - q), prec, round(tp / len(truth), 4)])
with (out / f"alleles_{tag}.tsv").open("w") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["chrom", "pos", "ref", "alt", *CALLERS, "benchmark"])
    for v in sorted(set.union(*sets.values(), truth)):
        w.writerow([*v, *[int(v in s) for s in sets.values()],
                    ("match" if v in truth else "absent") if inside(v) else "outside"])
print(open(out / f"benchmark_{tag}.tsv").read())
