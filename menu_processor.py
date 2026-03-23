import csv
from menu_loader import norm, sim, load_items, load_online

ITEMS_FILE = 'items_114325_2026_03_23_02_22_23.csv'
ONLINE_FILE = 'Menu-data.csv'
MENU_FILE = 'menu_import.csv'
OUT_FILE = 'updated_menu_import.csv'
MATCH_THRESHOLD = 0.78


def find_online_key(name, variation, online):
    vkey = norm(variation) if variation else ''
    best_key, best_ratio = None, 0
    for (cn, vn) in online:
        if vn != vkey:
            continue
        r = sim(name, cn)
        if r > best_ratio:
            best_ratio, best_key = r, (cn, vn)
    return best_key if best_ratio >= MATCH_THRESHOLD else None


def find_items_data(name, sc, by_code, by_name):
    if sc and sc in by_code:
        return by_code[sc]
    nn = norm(name)
    best_data, best_ratio = None, 0
    for k, v in by_name.items():
        r = sim(nn, k)
        if r > best_ratio:
            best_ratio, best_data = r, v
    return best_data if best_ratio >= 0.88 else None


def main():
    by_code, by_name = load_items(ITEMS_FILE)
    online = load_online(ONLINE_FILE)

    output_rows, fieldnames = [], None
    sw_updated, base_updated = 0, 0
    unmatched = set(online.keys())

    with open(MENU_FILE, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            name = row['name'].strip()
            sc = row['short_code'].strip()
            variation = row['variation'].strip()

            # Step 2: update swiggy / zomato from online catalogue
            key = find_online_key(name, variation, online)
            if key and key in online:
                price = online[key]
                row['swiggy'] = price
                row['zomato'] = price
                sw_updated += 1
                unmatched.discard(key)

            # Step 3: update base_price from items CSV
            idata = find_items_data(name, sc, by_code, by_name)
            if idata:
                if variation and variation in idata['variations']:
                    new_p = idata['variations'][variation]
                elif not variation:
                    new_p = idata['price']
                else:
                    new_p = None
                if new_p is not None:
                    try:
                        old_p = int(row['base_price']) if row['base_price'] else None
                    except ValueError:
                        old_p = None
                    if old_p != new_p:
                        row['base_price'] = new_p
                        base_updated += 1

            # Step 4: parcel_price = base_price
            row['parcel_price'] = row['base_price']
            output_rows.append(row)

    with open(OUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\n{'='*55}")
    print(f"  SUMMARY REPORT")
    print(f"{'='*55}")
    print(f"  Swiggy/Zomato rows updated : {sw_updated}")
    print(f"  Base price rows updated    : {base_updated}")
    print(f"\n  Unmatched online items ({len(unmatched)}):")
    for k in sorted(unmatched):
        print(f"    - catalogue='{k[0]}' variant='{k[1]}'")
    print(f"{'='*55}")
    print(f"\n  Output written to: {OUT_FILE}\n")


if __name__ == '__main__':
    main()
