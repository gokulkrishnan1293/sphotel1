"""
Manual patches for the 12 unmatched online items and 1 wrong match.
Reads updated_menu_import.csv, applies fixes, overwrites in place.
"""
import csv

# (menu item name, variation) -> (swiggy_price, zomato_price)
PATCHES = {
    ('Idly [2 Nos]',              ''): (55,  55),
    ('Hot & Sour Veg Soup',       ''): (100, 100),
    ('Hot & Sour Non-Veg Soup',   ''): (115, 115),
    ('Noodles Soup Veg Soup',     ''): (115, 115),
    ('Noodles Soup Non-Veg Soup', ''): (140, 140),
    ('Omlet',                     ''): (50,  50),
    ('Veg Kothu [Veg Special]',   ''): (115, 115),
    ('Sp',                        ''): (150, 150),
    ('Egg Kothu [special]',       ''): (130, 130),
    ('Shawarma Roll',             ''): (150, 150),
    ('Shawarma Plate',            ''): (180, 180),
    # Wrong match: Schezwan Veg Fried Rice was matched to Schezwan Egg Fried Rice
    # Correct: Schezwan Fried Rice online = 160
    ('Schezwan Veg Fried Rice',   ''): (160, 160),
}

FILE = 'updated_menu_import.csv'
patched = 0
rows = []
fieldnames = None

with open(FILE, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        key = (row['name'].strip(), row['variation'].strip())
        if key in PATCHES:
            sw, zo = PATCHES[key]
            if int(row['swiggy'] or 0) != sw or int(row['zomato'] or 0) != zo:
                row['swiggy'] = sw
                row['zomato'] = zo
                patched += 1
        rows.append(row)

with open(FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Patched {patched} rows manually. File updated: {FILE}")
