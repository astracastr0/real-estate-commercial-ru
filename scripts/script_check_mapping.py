#!/usr/bin/env python3
"""
Check fresh JSON files for district/underground IDs missing from the mapping.
Run from anywhere — finds the latest 2026 sale folder for each area.

Usage:
    python3 scripts/script_check_mapping.py
"""

import json
import glob
import os

# Mirror of districts_undergrounds_mapping from script1_get_sale_rent_offers.py
MAPPING = {
    "NAO":   {"districts": [325,327,328,329,330,331,332,333,334,335,336,337],
              "undergrounds": [23,25,127,136,138,284,285,364,365,366,367,377,378,379,380,406,434,435,436,437,438,494,495,496,497,498,499,500,502,535,536,538,543,545,546,547,551,552,553,557]},
    "CAO":   {"districts": [4,13,14,15,16,17,18,19,20,21,22],
              "undergrounds": [4,8,12,13,14,15,18,20,31,33,38,46,47,50,53,54,55,56,58,61,63,64,66,68,70,71,72,77,78,80,84,85,86,95,96,98,101,103,105,107,108,110,114,115,117,118,119,121,123,124,125,129,130,132,134,143,145,148,149,150,151,155,159,236,237,272,310,311,381,384,385,386,395,396,400,425,426,441,446,451,453,470,512,514,515,518,519,520,540]},
    "VAO":   {"districts": [7,56,57,59,60,61,62,63,64,65,66,67,68,69,70,71],
              "undergrounds": [1,34,41,53,76,88,89,90,100,107,113,117,137,146,152,153,155,243,298,299,300,301,302,371,372,373,384,385,386,443,470,471,472,473,474,477,478,479,480,481,522,523,524,526,527,529,530,531,539]},
    "ZAO":   {"districts": [11,112,113,114,115,116,117,118,119,120,121,122,123,124,348,349,350],
              "undergrounds": [11,35,46,57,60,62,70,72,87,93,102,115,120,140,141,142,156,228,233,234,272,281,311,337,338,339,361,362,363,364,365,366,391,392,393,394,395,401,402,403,404,405,417,419,440,444,447,450,453,498,499,502,503,504,505,506,507,508,509,510,511,532,535,541,548,549,563]},
    "SAO":   {"districts": [5,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38],
              "undergrounds": [9,14,15,28,29,30,36,37,68,71,81,91,97,106,110,116,128,134,286,289,290,291,292,293,294,295,296,311,349,350,351,352,353,354,369,383,398,399,408,412,413,414,422,423,424,451,453,457,458,459,460,461,462,463,464,465,466,467,514,515,534]},
    "SZAO":  {"districts": [125,126,127,128,129,130,131,132],
              "undergrounds": [30,57,72,81,94,97,122,133,154,228,233,234,235,244,275,289,290,291,292,311,351,395,396,420,421,422,440,453,460,461,512,558,559,560,562,563]},
    "SVAO":  {"districts": [6,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55],
              "undergrounds": [5,6,10,15,17,21,27,28,37,69,71,78,83,91,107,110,111,128,236,237,286,287,296,297,298,353,384,399,409,410,411,412,413,414,451,454,467,468,515,516,533,534,537]},
    "UVAO":  {"districts": [8,72,73,74,75,76,77,78,79,80,81,82,83],
              "undergrounds": [1,2,22,31,32,34,40,48,55,59,65,67,92,95,101,108,109,126,240,270,271,282,302,303,304,305,370,371,372,373,374,375,376,425,426,427,428,429,439,443,448,449,452,471,472,473,474,475,476,477,478,479,482,485,520,521,522]},
    "UAO":   {"districts": [9,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99],
              "undergrounds": [2,7,19,24,26,38,39,40,43,44,45,48,49,52,55,63,73,74,75,82,85,99,101,112,114,131,135,139,144,147,151,157,238,239,240,245,273,274,283,306,307,308,309,387,388,430,431,432,433,445,554,556,565,566,567,568,569,570,571,573]},
    "UZAO":  {"districts": [10,100,101,102,103,104,105,106,107,108,109,110,111],
              "undergrounds": [3,7,16,19,23,24,25,33,42,51,63,74,75,79,102,104,127,136,138,139,140,156,158,273,274,281,308,309,389,390,391,434,437,438,450,538,541,548,549,550,554,555]},
    "ZelAO": {"districts": [151,152,153,154,355,356,357,358],
              "undergrounds": [455,456,457]},
    "TAO":   {"districts": [326,338,339,340,341,342,343,344,345,346,347],
              "undergrounds": []},
}

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "step1_json_data")


def collect_ids(folder):
    districts, undergrounds = set(), set()
    for f in glob.glob(os.path.join(folder, "*.json")):
        try:
            offers = json.load(open(f, encoding="utf-8"))["data"]["offersSerialized"]
            for o in offers:
                geo = o.get("geo", {})
                for d in geo.get("districts", []):
                    if d.get("type") == "raion":
                        districts.add((d["id"], d.get("name", "")))
                for g in geo.get("undergrounds", []):
                    undergrounds.add((g["id"], g.get("name", "")))
        except Exception:
            pass
    return districts, undergrounds


def main():
    print("=" * 60)
    print("Mapping check — new districts & undergrounds")
    print("=" * 60)

    # Build global sets of all known IDs across all areas
    all_known_districts   = set(d for m in MAPPING.values() for d in m["districts"])
    all_known_undergrounds = set(u for m in MAPPING.values() for u in m["undergrounds"])

    found_any = False

    for area, m in MAPPING.items():
        folders = sorted(glob.glob(os.path.join(BASE_DIR, f"json_files_sale_{area}_26????")))
        if not folders:
            print(f"[NO DATA] {area}")
            continue

        districts, undergrounds = collect_ids(folders[-1])

        # Truly new = not in THIS area AND not in ANY other area
        new_d = sorted(x for x in districts    if x[0] not in m["districts"]      and x[0] not in all_known_districts)
        new_u = sorted(x for x in undergrounds if x[0] not in m["undergrounds"]   and x[0] not in all_known_undergrounds)

        # Border effect = not in THIS area but already covered elsewhere
        border_d = sorted(x for x in districts    if x[0] not in m["districts"]    and x[0] in all_known_districts)
        border_u = sorted(x for x in undergrounds if x[0] not in m["undergrounds"] and x[0] in all_known_undergrounds)

        if new_d or new_u:
            found_any = True
            print(f"\n[NEW - ADD TO MAPPING] {area}  (folder: {os.path.basename(folders[-1])})")
            if new_d:
                print(f"  districts:    {new_d}")
            if new_u:
                print(f"  undergrounds: {new_u}")
        elif border_d or border_u:
            print(f"[BORDER]  {area} — covered by other areas, skip")
            if border_d:
                print(f"  districts already elsewhere:    {border_d}")
            if border_u:
                print(f"  undergrounds already elsewhere: {border_u}")
        else:
            print(f"[OK]  {area}  ({len(districts)} dist, {len(undergrounds)} metro)")

    print()
    if not found_any:
        print("All good — no truly new IDs found.")
    else:
        print("Add the IDs marked [NEW] to MAPPING in this script AND to")
        print("districts_undergrounds_mapping in script1_get_sale_rent_offers.py")


if __name__ == "__main__":
    main()
