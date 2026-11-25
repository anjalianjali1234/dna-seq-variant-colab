"""Annotate called alleles with Ensembl VEP (GRCh37 REST API), with an offline fallback.

Usage: python scripts/annotate.py [alleles_tsv]
Default input: run/report/alleles_q30_dp10.tsv. Output: run/report/annotated.tsv
If the live API is unreachable, the frozen snapshot data/vep.tsv (Ensembl release 116) is used.
"""
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "run/report/alleles_q30_dp10.tsv")
rows = [r for r in csv.DictReader(src.open(), delimiter="\t")
        if "1" in (r.get("gatk"), r.get("bcftools"), r.get("freebayes"))]
key = lambda r: (r["chrom"], r["pos"], r["ref"], r["alt"])
BASE = "https://grch37.rest.ensembl.org"

def post(variants):
    req = urllib.request.Request(BASE + "/vep/human/region?af_gnomadg=1",
                                 data=json.dumps({"variants": variants}).encode(),
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=120))

def live():
    ann = {}
    vcf_lines = [f"{r['chrom'].replace('chr', '')} {r['pos']} . {r['ref']} {r['alt']} . . ." for r in rows]
    for i in range(0, len(vcf_lines), 50):
        for v in post(vcf_lines[i:i + 50]):
            c, p, _, ref, alt, *_ = v["input"].split()
            vref, valt = v["allele_string"].split("/")[0], v["allele_string"].split("/")[-1]
            tx = [t for t in v.get("transcript_consequences", []) if v["most_severe_consequence"] in t["consequence_terms"]]
            genes = sorted({t["gene_symbol"] for t in tx if "gene_symbol" in t})
            col = [x for x in v.get("colocated_variants", []) if x.get("start") == v["start"] and x.get("end") == v["end"]]
            ids = sorted({x["id"] for x in col if x.get("id", "").startswith("rs")})
            afs = {x["frequencies"][valt]["gnomadg"] for x in col if "gnomadg" in x.get("frequencies", {}).get(valt, {})}
            ann[("chr" + c, p, ref, alt)] = {
                "consequence": v["most_severe_consequence"], "genes": ",".join(genes) or ".",
                "rs_ids": ",".join(ids) or ".", "gnomad_genomes_af": str(next(iter(afs))) if len(afs) == 1 else ".",
                "clinvar_lookup": ("https://www.ncbi.nlm.nih.gov/clinvar/?term=" + ids[0]) if ids else "."}
        time.sleep(1)
    return ann, "live Ensembl VEP REST (GRCh37)"

try:
    ann, source = live()
except Exception as e:  # network or API problem -> frozen snapshot
    print("Live VEP unavailable (", e, ") - using frozen snapshot data/vep.tsv")
    ann = {key(r): r for r in csv.DictReader(open("data/vep.tsv"), delimiter="\t")}
    source = "frozen snapshot data/vep.tsv (Ensembl release 116)"

extra = ["consequence", "genes", "rs_ids", "gnomad_genomes_af", "clinvar_lookup"]
out = Path("run/report/annotated.tsv")
with out.open("w") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]) + extra + ["frequency_group"], delimiter="\t", lineterminator="\n")
    w.writeheader()
    for r in rows:
        a = ann.get(key(r), {})
        r.update({k: a.get(k, ".") for k in extra})
        af = r["gnomad_genomes_af"]
        r["frequency_group"] = "unknown" if af == "." else ("rare_below_1pct" if float(af) < 0.01 else "common_at_least_1pct")
        w.writerow(r)
print(f"Annotated {len(rows)} alleles using {source} -> {out}")
