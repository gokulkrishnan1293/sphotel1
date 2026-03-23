import csv
import re
from difflib import SequenceMatcher


def norm(s):
    s = re.sub(r'[^a-z0-9 ]', ' ', str(s).lower().strip())
    return re.sub(r'\s+', ' ', s).strip()


def sim(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def _parse_row(row):
    """
    Detect and correct a 1-column left-shift that affects some items_csv rows.
    Symptom: row[2] is numeric (Short_Code leaked into Description) and row[3] is empty.
    Normal layout: Name[0], Online_Name[1], Description[2], Short_Code[3], …, Price[10]
    Shifted layout: same first two, Short_Code at [2], all subsequent cols -1.
    Returns (sc, price, var_pairs) where var_pairs is a list of (name, price) tuples.
    """
    # Detect shift: row[3] empty AND row[2] looks like a short code (digit or code)
    shifted = row[3].strip() == '' and row[2].strip() != ''
    sc_idx, price_idx = (2, 9) if shifted else (3, 10)
    var_pairs_idx = [(24, 25), (28, 29), (32, 33)] if shifted else [(25, 26), (29, 30), (33, 34)]

    sc = row[sc_idx].strip()
    try:
        price = int(float(row[price_idx]))
    except (ValueError, IndexError):
        price = 0

    variations = {}
    for vi, pi in var_pairs_idx:
        if len(row) > pi:
            vn = row[vi].strip()
            vp_str = row[pi].strip()
            if vn and vp_str:
                try:
                    variations[vn] = int(float(vp_str))
                except ValueError:
                    pass
    return sc, price, variations


def load_items(path):
    """
    Returns (by_code, by_name):
      by_code: {short_code_str -> {price, name, variations:{var_name: price}}}
      by_name: {normalized_name -> same dict}
    """
    by_code, by_name = {}, {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) < 10:
                continue
            name = row[0].strip()
            sc, price, variations = _parse_row(row)
            data = {'price': price, 'name': name, 'variations': variations}
            if sc:
                by_code[sc] = data
            if name:
                by_name[norm(name)] = data
    return by_code, by_name


def load_online(path):
    """
    Returns dict: (norm_catalogue_name, norm_variant_or_empty) -> price
    Simple items (variant_name == catalogue_name) get key with empty variant.
    Items with variants get key with the norm'd variant name.
    """
    online = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            cat = row['catalogue_name'].strip()
            var = row['variant_name'].strip()
            try:
                price = int(float(row['current_price']))
            except (ValueError, KeyError):
                continue
            vkey = '' if norm(cat) == norm(var) else norm(var)
            online[(norm(cat), vkey)] = price
    return online
