#!/usr/bin/env python3
"""
Estimate the ad valorem revenue a Florida county or municipality loses to the
2026 Amendment 3 homestead exemption (HJR 1-F), parcel by parcel, from the
Florida Department of Revenue NAL (Name-Address-Legal) tax roll file.

Standard library only, so it runs in any sandbox (Claude, ChatGPT, local).

Usage examples
--------------
  # A city: select its parcels by the property appraiser's taxing-authority code(s)
  python exemption_impact.py NAL62F202601.csv --levy municipal \
      --tax-auth LA --millage 5.52 --name "City of Largo"

  # A county's countywide levy: every parcel in the file
  python exemption_impact.py NAL48F202601.csv --levy county --millage 4.4347

  # Find the taxing-authority codes first:
  python exemption_impact.py NAL62F202601.csv --list-tax-auth --city LARGO

Method (read before relying on the numbers)
-------------------------------------------
For each homestead parcel (EXMPT_01 > 0):
  * Today, non-school levies get EXMPT_01 (first $25,000) + EXMPT_02 (the
    additional exemption, up to $26,411 in 2026, applied to value between
    $50,000 and ~$76,411).
  * Under Amendment 3 those two are replaced, for non-school levies, by one
    exemption "up to the assessed valuation of" $150,000 (2027) and $250,000
    (2028), applied from the first dollar.
  * New exemption = min(homestead assessed value, cap). Other exemptions on the
    parcel (seniors, widows, disability, etc.) are left as they are, and the
    parcel's taxable value cannot go below zero.
  * Lost revenue = (old taxable value - new taxable value) x millage / 1000.

Known limits the user must state alongside any result:
  1. New residents: anyone who was not a Florida resident on Dec. 31, 2026 gets
     only $50,000 for five years. The NAL file cannot identify them, so this
     overstates the loss slightly, and the overstatement grows over time as
     new homesteads are created.
  2. The 5% non-homestead assessment cap (down from 10%) is not modeled here;
     it reduces FUTURE growth, not today's base. Use --nonhomestead-growth to
     sketch it.
  3. Static roll: no growth, sales, or new construction between the roll year
     and the impact year. The city's own budget office will have a better
     forward projection; use this to check it, not to replace it.
  4. Tax increment (CRA) and dependent-district impacts are not computed.
  5. Values are at 100%; budgets are adopted at no less than 95% of the
     levy (s. 200.065(2)(a)1., F.S.). Use --collection-rate to match the
     budget.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sys

# Exemption columns that apply ONLY to county levies (so a city's taxable value
# is higher than TV_NSD by these) and ONLY to municipal levies (so a city's
# taxable value is lower than TV_NSD by these). Source: 2026 NAL/SDF/NAP
# User's Guide, "NAL Exemptions" table (applicable-to columns).
COUNTY_ONLY = ["EXMPT_03", "EXMPT_10", "EXMPT_22", "EXMPT_24", "EXMPT_39", "EXMPT_45"]
MUNICIPAL_ONLY = ["EXMPT_04", "EXMPT_11", "EXMPT_23", "EXMPT_25", "EXMPT_40", "EXMPT_46"]

# DOR use-code groups (DOR_UC, "000"-"099") for the class breakdown.
USE_GROUPS = [
    (0, 9, "Residential"),
    (10, 39, "Commercial"),
    (40, 49, "Industrial"),
    (50, 69, "Agricultural"),
    (70, 79, "Institutional"),
    (80, 89, "Governmental"),
    (90, 99, "Misc./Centrally assessed"),
]


def num(row: dict, key: str) -> int:
    v = (row.get(key) or "").strip()
    if not v:
        return 0
    try:
        return int(float(v))
    except ValueError:
        return 0


def use_group(dor_uc: str) -> str:
    try:
        code = int((dor_uc or "").strip() or -1)  # DOR_UC is "000"-"099"
    except ValueError:
        return "Unknown"
    for lo, hi, name in USE_GROUPS:
        if lo <= code <= hi:
            return name
    return "Unknown"


def levy_taxable(row: dict, levy: str) -> int:
    """Current taxable value for the chosen non-school levy."""
    tv = num(row, "TV_NSD")  # county taxable value
    if levy == "municipal":
        tv += sum(num(row, k) for k in COUNTY_ONLY)
        tv -= sum(num(row, k) for k in MUNICIPAL_ONLY)
    return max(tv, 0)


def new_taxable(row: dict, levy: str, cap: int) -> int:
    """Taxable value for the chosen levy once the exemption is `cap`."""
    old = levy_taxable(row, levy)
    if num(row, "EXMPT_01") <= 0:  # not a homestead
        return old
    current_hx = num(row, "EXMPT_01") + num(row, "EXMPT_02")
    hx_base = num(row, "AV_HMSTD") or num(row, "AV_NSD")
    new_hx = min(hx_base, cap)
    return max(old + current_hx - new_hx, 0)


def run(args: argparse.Namespace) -> dict:
    tax_auth = {c.strip().upper() for c in (args.tax_auth or [])}
    caps = {"2027 ($150,000)": 150_000, "2028 ($250,000)": args.cap_2028}

    totals = collections.Counter()
    by_class = collections.defaultdict(collections.Counter)
    homestead_bands = collections.Counter()

    with open(args.nal, newline="", encoding="latin-1") as f:
        for row in csv.DictReader(f):
            if tax_auth and row.get("TAX_AUTH_CD", "").strip().upper() not in tax_auth:
                continue
            old = levy_taxable(row, args.levy)
            grp = use_group(row.get("DOR_UC", ""))
            is_hx = num(row, "EXMPT_01") > 0
            totals["parcels"] += 1
            totals["taxable_now"] += old
            by_class[grp]["parcels"] += 1
            by_class[grp]["taxable_now"] += old
            if is_hx:
                totals["homestead_parcels"] += 1
                hx_av = num(row, "AV_HMSTD") or num(row, "AV_NSD")
                band = ("<$150k" if hx_av < 150_000 else
                        "$150k-$250k" if hx_av < 250_000 else ">=$250k")
                homestead_bands[band] += 1
            for label, cap in caps.items():
                new = new_taxable(row, args.levy, cap)
                totals[f"taxable_{label}"] += new
                by_class[grp][f"taxable_{label}"] += new
                if is_hx and new == 0:
                    totals[f"homesteads_fully_exempt_{label}"] += 1

    mills = args.millage / 1000.0
    rate = args.collection_rate
    result = {
        "jurisdiction": args.name or ("tax_auth=" + ",".join(sorted(tax_auth)) if tax_auth else "all parcels"),
        "levy": args.levy,
        "millage": args.millage,
        "collection_rate": rate,
        "parcels": totals["parcels"],
        "homestead_parcels": totals["homestead_parcels"],
        "homestead_assessed_value_bands": dict(homestead_bands),
        "taxable_value_now": totals["taxable_now"],
        "levy_now": round(totals["taxable_now"] * mills * rate),
        "scenarios": {},
        "by_class": {},
        "assumptions": [
            "Static roll (no growth/new construction) at the roll year in the file.",
            "Exemption replaces EXMPT_01 + EXMPT_02 for non-school levies; other exemptions unchanged.",
            "New-resident $50,000 phase-in NOT modeled (overstates the loss).",
            "5% non-homestead cap NOT modeled (affects future growth, not today's base).",
            "CRA tax increment and dependent districts NOT included.",
        ],
    }
    for label in caps:
        new_tv = totals[f"taxable_{label}"]
        lost_tv = totals["taxable_now"] - new_tv
        result["scenarios"][label] = {
            "taxable_value": new_tv,
            "taxable_value_lost": lost_tv,
            "pct_of_taxable_value": round(100 * lost_tv / totals["taxable_now"], 2) if totals["taxable_now"] else 0,
            "revenue_lost_at_current_millage": round(lost_tv * mills * rate),
            "homesteads_fully_exempt": totals[f"homesteads_fully_exempt_{label}"],
            "millage_needed_to_hold_levy_flat": round(args.millage * totals["taxable_now"] / new_tv, 4) if new_tv else None,
        }
    for grp, c in sorted(by_class.items()):
        result["by_class"][grp] = {
            "parcels": c["parcels"],
            "taxable_now": c["taxable_now"],
            **{f"taxable_{lbl}": c[f"taxable_{lbl}"] for lbl in caps},
        }
    return result


def list_tax_auth(args: argparse.Namespace) -> None:
    counts, tv = collections.Counter(), collections.Counter()
    with open(args.nal, newline="", encoding="latin-1") as f:
        for row in csv.DictReader(f):
            if args.city and row.get("PHY_CITY", "").strip().upper() != args.city.upper():
                continue
            code = row.get("TAX_AUTH_CD", "").strip()
            counts[code] += 1
            tv[code] += num(row, "TV_NSD")
    print(f"{'TAX_AUTH_CD':<12}{'parcels':>10}{'TV_NSD':>20}")
    for code, n in counts.most_common():
        print(f"{code:<12}{n:>10}{tv[code]:>20,}")
    print("\nTAX_AUTH_CD codes are assigned by each property appraiser. Confirm which "
          "code(s) are the jurisdiction with the property appraiser's taxing-district "
          "table; a mailing city (PHY_CITY) is NOT the same as the city limits.")


def extract(args: argparse.Namespace) -> None:
    tax_auth = {c.strip().upper() for c in (args.tax_auth or [])}
    if not tax_auth:
        sys.exit("--extract needs --tax-auth to choose the parcels")
    n = 0
    with open(args.nal, newline="", encoding="latin-1") as f, \
         open(args.extract, "w", newline="", encoding="latin-1") as out:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if row.get("TAX_AUTH_CD", "").strip().upper() in tax_auth:
                writer.writerow(row)
                n += 1
    print(f"Wrote {n:,} parcels to {args.extract}")


def print_report(r: dict) -> None:
    print(f"\n{r['jurisdiction']}  ({r['levy']} levy, {r['millage']} mills, collection rate {r['collection_rate']})")
    print(f"Parcels: {r['parcels']:,}   Homestead parcels: {r['homestead_parcels']:,}")
    print(f"Homestead assessed-value bands: {r['homestead_assessed_value_bands']}")
    print(f"Taxable value now: ${r['taxable_value_now']:,}   Levy now: ${r['levy_now']:,}")
    for label, s in r["scenarios"].items():
        print(f"\n  {label}")
        print(f"    Taxable value lost:     ${s['taxable_value_lost']:,}  ({s['pct_of_taxable_value']}%)")
        print(f"    Revenue lost:           ${s['revenue_lost_at_current_millage']:,} per year")
        print(f"    Homesteads paying $0:   {s['homesteads_fully_exempt']:,}")
        print(f"    Millage to hold levy:   {s['millage_needed_to_hold_levy_flat']}")
        m = s["millage_needed_to_hold_levy_flat"]
        if m and m > 10:
            print("    NOTE: above the 10-mill constitutional cap for county or municipal purposes "
                  "(Art. VII, s. 9(b)); raising the tax rate cannot replace this loss on its own.")
    print("\n  Taxable value by property class (now -> 2028):")
    for grp, c in r["by_class"].items():
        print(f"    {grp:<26}{c['parcels']:>8,} parcels  ${c['taxable_now']:>16,} -> ${c['taxable_2028 ($250,000)']:>16,}")
    print("\n  Assumptions:")
    for a in r["assumptions"]:
        print(f"    - {a}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("nal", help="Path to the DOR NAL CSV (e.g. NAL62F202601.csv)")
    p.add_argument("--levy", choices=["county", "municipal"], default="municipal")
    p.add_argument("--tax-auth", nargs="*", help="TAX_AUTH_CD code(s) that make up the jurisdiction")
    p.add_argument("--millage", type=float, help="Operating millage for the levy")
    p.add_argument("--collection-rate", type=float, default=1.0,
                   help="Fraction of the levy budgeted (e.g. 0.96). Default 1.0")
    p.add_argument("--cap-2028", type=int, default=250_000,
                   help="Exemption for 2028 (default 250000). Indexed for inflation from 2029.")
    p.add_argument("--name", help="Label for the report")
    p.add_argument("--json", help="Also write the full result to this JSON path")
    p.add_argument("--extract", help="Write only the selected parcels (all columns) to this CSV and exit. "
                                     "Use to make a small file you can upload to a chat.")
    p.add_argument("--list-tax-auth", action="store_true", help="List TAX_AUTH_CD codes and exit")
    p.add_argument("--city", help="With --list-tax-auth: filter by physical-address city")
    args = p.parse_args()

    if args.list_tax_auth:
        list_tax_auth(args)
        return
    if args.extract:
        extract(args)
        return
    if args.millage is None:
        p.error("--millage is required (the jurisdiction's adopted operating millage)")
    r = run(args)
    print_report(r)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2)
        print(f"\nWrote {args.json}")


if __name__ == "__main__":
    sys.exit(main())
