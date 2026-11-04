#!/usr/bin/env python3
"""
Who pays more, who pays less: compare each property's property-tax savings
under Amendment 3 with the new charges in a proposed package, and estimate the
revenue each charge would raise. Reads the same DOR NAL file as
exemption_impact.py. Standard library only.

Usage
-----
  python incidence.py NAL62F202601.csv --tax-auth LA --levy municipal \
      --millage 5.52 --package package.json

package.json describes the proposed charges (see PACKAGE FORMAT below, or run
with --example-package to print a starter file). All rates are proposals the
user supplies or chooses; this script does not set them.

Output
------
  1. Revenue each charge would raise, by property category, and which parcels
     are exempt or bought down.
  2. For each property category: average property-tax savings vs. average new
     charges, and how many parcels come out ahead or behind.
  3. Sample properties (median homestead under $250k assessed value, median
     homestead over $250k, a condo, a rental, a small and a large commercial
     building, an industrial building, a religious/charitable parcel): what each
     saves, what each would pay, and the net.

PACKAGE FORMAT
--------------
{
  "name": "Middle path",
  "charges": [
    {
      "name": "Fire assessment",
      "rates": {
        "residential":   {"per": "unit", "rate": 180},
        "commercial":    {"per": "sqft_tier", "tiers": [[0, 1999, 250], [2000, 9999, 900], [10000, null, 2500]]},
        "industrial":    {"per": "sqft_tier", "tiers": [[0, 9999, 600], [10000, null, 1800]]},
        "institutional": {"per": "sqft_tier", "tiers": [[0, 9999, 300], [10000, null, 900]], "bought_down": true},
        "vacant":        {"per": "parcel", "rate": 25},
        "agricultural":  {"per": "parcel", "rate": 25},
        "government":    {"exempt": true}
      }
    }
  ]
}
"per" may be "unit" (residential units; at least 1 per improved residential
parcel), "parcel", "sqft" (rate per square foot), or "sqft_tier" (flat amount
by building-area range; null upper bound = no limit). "exempt" = not charged.
"bought_down" = charged in the roll but paid from other revenue (shown
separately; the owner pays nothing).

Limits: building area comes from TOT_LVG_AREA (the appraiser's "effective"
area, which may weight garages/offices); the property appraiser's building
file is better for a real rate study. Unit counts come from NO_RES_UNTS.
Amendment 3 savings use the same method and limits as exemption_impact.py.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exemption_impact import levy_taxable, new_taxable, num  # noqa: E402

VACANT = {0, 10, 40, 70, 80}

EXAMPLE = {
    "name": "Example package (replace every rate with the user's choices)",
    "charges": [{
        "name": "Fire assessment",
        "rates": {
            "residential": {"per": "unit", "rate": 0},
            "commercial": {"per": "sqft_tier", "tiers": [[0, 1999, 0], [2000, 9999, 0], [10000, None, 0]]},
            "industrial": {"per": "sqft_tier", "tiers": [[0, 9999, 0], [10000, None, 0]]},
            "institutional": {"per": "sqft_tier", "tiers": [[0, 9999, 0], [10000, None, 0]], "bought_down": True},
            "vacant": {"per": "parcel", "rate": 0},
            "agricultural": {"per": "parcel", "rate": 0},
            "government": {"exempt": True},
        },
    }],
}


def category(row: dict) -> str:
    try:
        code = int((row.get("DOR_UC") or "").strip())
    except ValueError:
        return "other"
    if code in VACANT:
        return "vacant"
    if 1 <= code <= 9:
        return "residential"
    if 11 <= code <= 39:
        return "commercial"
    if 41 <= code <= 49:
        return "industrial"
    if 50 <= code <= 69:
        return "agricultural"
    if 71 <= code <= 79:
        return "institutional"
    if 81 <= code <= 89:
        return "government"
    return "other"


def charge_for(row: dict, rule: dict) -> float:
    if not rule or rule.get("exempt"):
        return 0.0
    per = rule.get("per")
    if per == "parcel":
        return float(rule["rate"])
    if per == "unit":
        return float(rule["rate"]) * max(num(row, "NO_RES_UNTS"), 1)
    area = num(row, "TOT_LVG_AREA")
    if per == "sqft":
        return float(rule["rate"]) * area
    if per == "sqft_tier":
        for lo, hi, amount in rule["tiers"]:
            if area >= lo and (hi is None or area <= hi):
                return float(amount)
        return 0.0
    raise ValueError(f"Unknown 'per': {per}")


def run(args: argparse.Namespace) -> dict:
    with open(args.package, encoding="utf-8") as f:
        package = json.load(f)
    tax_auth = {c.strip().upper() for c in (args.tax_auth or [])}
    mills = args.millage / 1000.0

    revenue = collections.defaultdict(lambda: collections.Counter())
    bought_down = collections.Counter()
    by_cat = collections.defaultdict(lambda: {"n": 0, "saved": 0.0, "charged": 0.0, "ahead": 0, "behind": 0})
    pools = collections.defaultdict(list)

    with open(args.nal, newline="", encoding="latin-1") as f:
        for row in csv.DictReader(f):
            if tax_auth and row.get("TAX_AUTH_CD", "").strip().upper() not in tax_auth:
                continue
            cat = category(row)
            saved = (levy_taxable(row, args.levy) - new_taxable(row, args.levy, args.cap)) * mills
            owner_pays = 0.0
            for ch in package["charges"]:
                rule = ch["rates"].get(cat)
                amt = charge_for(row, rule)
                if rule and rule.get("bought_down"):
                    bought_down[ch["name"]] += amt
                else:
                    owner_pays += amt
                    revenue[ch["name"]][cat] += amt
            b = by_cat[cat]
            b["n"] += 1
            b["saved"] += saved
            b["charged"] += owner_pays
            if owner_pays - saved > 0.5:
                b["behind"] += 1
            elif saved - owner_pays > 0.5:
                b["ahead"] += 1

            homestead = num(row, "EXMPT_01") > 0
            av = num(row, "AV_HMSTD") or num(row, "AV_NSD")
            code = (row.get("DOR_UC") or "").strip()
            area = num(row, "TOT_LVG_AREA")
            rec = (av, saved, owner_pays, row.get("PARCEL_ID", ""), area)
            if homestead and code == "001":
                pools["Homestead house, assessed under $250k" if av < 250_000 else
                      "Homestead house, assessed $250k or more"].append(rec)
            elif homestead and code == "004":
                pools["Homestead condo"].append(rec)
            elif not homestead and code == "001":
                pools["Non-homestead house (rental/second home)"].append(rec)
            elif cat == "commercial" and 0 < area < 5000:
                pools["Small commercial building (<5,000 sq ft)"].append(rec)
            elif cat == "commercial" and area >= 20000:
                pools["Large commercial building (20,000+ sq ft)"].append(rec)
            elif cat == "industrial" and area > 0:
                pools["Industrial/warehouse building"].append(rec)
            elif code == "071":
                pools["Church/religious property"].append(rec)

    samples = {}
    for label, recs in pools.items():
        recs.sort(key=lambda r: r[0])
        av, saved, charged, pid, area = recs[len(recs) // 2]
        samples[label] = {"parcel_id": pid, "assessed_value": av, "building_area": area,
                          "property_tax_saved": round(saved), "new_charges": round(charged),
                          "net_change": round(charged - saved), "parcels_in_group": len(recs)}

    return {
        "package": package.get("name", ""),
        "revenue_by_charge": {k: {"total": round(sum(v.values())), **{c: round(x) for c, x in v.items()}}
                              for k, v in revenue.items()},
        "bought_down_from_other_revenue": {k: round(v) for k, v in bought_down.items()},
        "by_category": {c: {"parcels": b["n"], "avg_tax_saved": round(b["saved"] / b["n"]) if b["n"] else 0,
                            "avg_new_charges": round(b["charged"] / b["n"]) if b["n"] else 0,
                            "pay_less_overall": b["ahead"], "pay_more_overall": b["behind"]}
                        for c, b in sorted(by_cat.items())},
        "samples (median of each group)": samples,
        "notes": [
            f"Property-tax savings at {args.millage} mills with a ${args.cap:,} exemption, static roll.",
            "Savings count only this government's levy, not county, school or district taxes.",
            "Building area is the appraiser's effective area (TOT_LVG_AREA), an approximation.",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("nal", nargs="?")
    p.add_argument("--package", help="Package JSON (see PACKAGE FORMAT)")
    p.add_argument("--levy", choices=["county", "municipal"], default="municipal")
    p.add_argument("--tax-auth", nargs="*")
    p.add_argument("--millage", type=float)
    p.add_argument("--cap", type=int, default=250_000, help="Exemption amount to compare against")
    p.add_argument("--json", help="Write the result to this JSON path")
    p.add_argument("--example-package", action="store_true", help="Print a starter package file and exit")
    args = p.parse_args()
    if args.example_package:
        print(json.dumps(EXAMPLE, indent=2))
        return
    if not (args.nal and args.package and args.millage is not None):
        p.error("nal, --package and --millage are required")
    r = run(args)
    print(json.dumps(r, indent=2))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2)


if __name__ == "__main__":
    main()
