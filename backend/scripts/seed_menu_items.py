"""
Seed script: Import menu items from CSV into the platform tenant.

Usage (dev):
  docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend \\
    sh -c "PYTHONPATH=/app python /app/scripts/seed_menu_items.py"

Usage (prod — pass credentials via env):
  SEED_TENANT_SLUG=sphotel python /app/scripts/seed_menu_items.py

The script is idempotent — skips items that already exist by (tenant_id, name, category).
Short codes that are not pure integers (e.g. "34(s)", "NCPA") are stored as NULL.
Prices from CSV are in rupees; stored as paise (×100).
"""
import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings

SEED_TENANT_SLUG = os.getenv("SEED_TENANT_SLUG", "sphotel")

# fmt: off
# Columns: name, short_code (str — null if non-numeric), category, price_rupees, food_type_raw, display_order
MENU_ITEMS = [
    ("Idly [2 Nos]",                    "1",          "Idli Varities",          25,  "veg",     1),
    ("Sambar Idly",                      "2",          "Idli Varities",          40,  "veg",     1),
    ("Fried Idly",                       "384",        "Idli Varities",          60,  "veg",     1),
    ("Chilly Idly",                      "456",        "Idli Varities",          70,  "veg",     1),
    ("Plain Dosai",                      "303",        "Dosai Varities",         30,  "veg",     1),
    ("Kal Dosai",                        "4",          "Dosai Varities",         30,  "veg",     1),
    ("Roast",                            "3",          "Dosai Varities",         60,  "veg",     1),
    ("Podi Dosai",                       "5",          "Dosai Varities",         40,  "veg",     1),
    ("Podi Roast",                       "418",        "Dosai Varities",         70,  "veg",     1),
    ("Tomato Uthappam",                  "7",          "Dosai Varities",         70,  "veg",     1),
    ("Egg Dosai",                        "8",          "Dosai Varities",         50,  "egg",     1),
    ("Egg Roast",                        "309",        "Dosai Varities",         80,  "egg",     1),
    ("Onion Roast",                      "10",         "Dosai Varities",         90,  "veg",     1),
    ("Masal Roast",                      "12",         "Dosai Varities",         90,  "veg",     1),
    ("Ghee Roast",                       "9",          "Dosai Varities",        100,  "veg",     1),
    ("Onion Ghee Roast",                 "11",         "Dosai Varities",        120,  "veg",     1),
    ("Ghee Masal Roast",                 "475",        "Dosai Varities",        130,  "veg",     1),
    ("Paneer Roast",                     "13",         "Dosai Varities",        120,  "veg",     1),
    ("Gobi Roast",                       "14",         "Dosai Varities",        110,  "veg",     1),
    ("Mushroom Roast",                   "15",         "Dosai Varities",        120,  "veg",     1),
    ("Chicken Kari Roast",               "20",         "Dosai Varities",        170,  "non-veg", 1),
    ("Mutton Kari Roast",                "21",         "Dosai Varities",        210,  "non-veg", 1),
    ("Plain Uthappam",                   "16",         "Dosai Varities",         60,  "veg",     1),
    ("Onion Uthappam",                   "18",         "Dosai Varities",         80,  "veg",     1),
    ("Veg Uthappam",                     "17",         "Dosai Varities",         80,  "veg",     1),
    ("Egg Uthappam",                     "19",         "Dosai Varities",         80,  "egg",     1),
    ("Egg Onion Rost",                   "467",        "Dosai Varities",         80,  "egg",     1),
    ("Parotta [1 Pc]",                   "75",         "Parotta Varities",       25,  "veg",     1),
    ("Ghee Parotta",                     "76",         "Parotta Varities",       40,  "veg",     1),
    ("Bun Parotta",                      "77",         "Parotta Varities",       40,  "veg",     1),
    ("Spl Sp",                           "312",        "Parotta Varities",      120,  "veg",     1),
    ("Plain Veehu Parotta",              "82",         "Parotta Varities",       35,  "veg",     1),
    ("Egg Vechu Parotta",                "83",         "Parotta Varities",       70,  "egg",     1),
    ("Veg Kothu [Veg Special]",          "84",         "Parotta Varities",       80,  "veg",     1),
    ("Egg Kothu [special]",              "34(s)",      "Parotta Varities",       90,  "egg",     1),
    ("Sp",                               "85",         "Parotta Varities",       90,  "veg",     1),
    ("Chicken S.P",                      "86",         "Parotta Varities",      170,  "non-veg", 1),
    ("Mutton S.P.",                      "423",        "Parotta Varities",      210,  "non-veg", 1),
    ("Chilly Parotta",                   "80",         "Parotta Varities",       90,  "veg",     1),
    ("Mushroom Stuff",                   "559",        "Parotta Varities",      100,  "veg",     1),
    ("Paneer Stuffed",                   "561",        "Parotta Varities",      110,  "veg",     1),
    ("Gobi Stuffed",                     "558",        "Parotta Varities",      100,  "veg",     1),
    ("Chicken Stuffed",                  "380",        "Parotta Varities",      120,  "veg",     1),
    ("Chappthi",                         "37",         "Parotta Varities",       25,  "veg",     1),
    ("Egg Chappthi",                     "38",         "Parotta Varities",       45,  "egg",     1),
    ("Egg Kothu Chappthi",               "579",        "Parotta Varities",       90,  "egg",     1),
    ("Mutton Kothu Chappthi",            "581",        "Parotta Varities",      200,  "non-veg", 1),
    ("Chicken Kothu Chaooathi",          "580",        "Parotta Varities",      160,  "non-veg", 1),
    ("Chicken Veechu Parotta",           "568",        "Parotta Varities",      200,  "non-veg", 1),
    ("Leaf Parotta",                     "575",        "Parotta Varities",      170,  "veg",     1),
    ("Veg Soup",                         "422",        "Soup Varities",          70,  "veg",     1),
    ("Veg Clear Soup",                   "43",         "Soup Varities",          70,  "veg",     1),
    ("Tomato Soup",                      "400",        "Soup Varities",          80,  "veg",     1),
    ("Mushroom Soup",                    "417",        "Soup Varities",          80,  "veg",     1),
    ("Chicken Milagu Soup",              "104",        "Soup Varities",          90,  "non-veg", 1),
    ("Chicken Clear Soup",               "101",        "Soup Varities",         100,  "non-veg", 1),
    ("Hot & Sour Veg Soup",              "103",        "Soup Varities",          90,  "veg",     1),
    ("Hot & Sour Non-Veg Soup",          "42",         "Soup Varities",         110,  "non-veg", 1),
    ("Noodles Soup Veg Soup",            "415",        "Soup Varities",          90,  "veg",     1),
    ("Noodles Soup Non-Veg Soup",        "416",        "Soup Varities",         110,  "non-veg", 1),
    ("Boiled Egg",                       "92",         "Egg Varities",           20,  "egg",     1),
    ("Plain Omlet",                      "88",         "Egg Varities",           20,  "egg",     1),
    ("Omlet",                            "166",        "Egg Varities",           25,  "egg",     1),
    ("Double Omlet",                     "389",        "Egg Varities",           50,  "egg",     1),
    ("Half Boil",                        "93",         "Egg Varities",           20,  "egg",     1),
    ("Full Boil",                        "94",         "Egg Varities",           20,  "egg",     1),
    ("Kalakki",                          "91",         "Egg Varities",           25,  "egg",     1),
    ("Other Kalakki",                    "459",        "Egg Varities",           30,  "egg",     1),
    ("Egg Podimas",                      "90",         "Egg Varities",           40,  "egg",     1),
    ("Egg Chilly",                       "406",        "Egg Varities",           90,  "egg",     1),
    ("Egg Masala",                       "89",         "Egg Varities",          100,  "egg",     1),
    ("One Side Omlet",                   "382",        "Egg Varities",           20,  "veg",     1),
    ("Veg Meals",                        "71",         "Meals",                 100,  "veg",     1),
    ("Cup Meals [After Biriyani]",       "72",         "Meals",                  60,  "veg",     1),
    ("Non Veg Meals",                    "200",        "Meals",                 250,  "veg",     1),
    ("Curd Rice",                        "73",         "Meals",                  60,  "veg",     1),
    ("Curd",                             "341",        "Meals",                  20,  "veg",     1),
    ("Kuska",                            "100",        "Biryani Varities",       70,  "veg",     1),
    ("Veg Briyani",                      "68",         "Biryani Varities",      100,  "veg",     1),
    ("Gobi Briyani",                     "429",        "Biryani Varities",      110,  "veg",     1),
    ("Paneer Briyani",                   "70",         "Biryani Varities",      140,  "veg",     1),
    ("Mushroom Briyani",                 "69",         "Biryani Varities",      130,  "veg",     1),
    ("Plain Briyani",                    "99",         "Biryani Varities",      100,  "veg",     1),
    ("Egg Briyani",                      "96",         "Biryani Varities",      140,  "egg",     1),
    ("Chicken Briyani",                  "97",         "Biryani Varities",      180,  "non-veg", 1),
    ("Chicken 65 Briyani",               "563",        "Biryani Varities",      190,  "non-veg", 1),
    ("Mutton Briyani",                   "98",         "Biryani Varities",      230,  "non-veg", 1),
    ("Fish Briyani",                     "364",        "Biryani Varities",      210,  "non-veg", 1),
    ("Kaadai Briyani",                   "562",        "Biryani Varities",      220,  "non-veg", 1),
    ("Prawn Briyani",                    "492",        "Biryani Varities",      250,  "non-veg", 1),
    ("Chilly Chiken Biriyani",           "564",        "Biryani Varities",      190,  "non-veg", 1),
    ("Nattukoli Biriyani",               "601",        "Biryani Varities",      250,  "non-veg", 1),
    ("Ghee Rice",                        "67",         "Fried Rice Varities",   100,  "veg",     1),
    ("Veg Fried Rice",                   "63",         "Fried Rice Varities",   110,  "veg",     1),
    ("Schezwan Veg Fried Rice",          "64",         "Fried Rice Varities",   120,  "veg",     1),
    ("Gobi Fried Rice",                  "434",        "Fried Rice Varities",   120,  "veg",     1),
    ("Schezwan Gobi Fried Rice",         "554",        "Fried Rice Varities",   130,  "veg",     1),
    ("Paneer Fried Rice",                "66",         "Fried Rice Varities",   140,  "veg",     1),
    ("Schezwan Paneer Fried Rice",       "480",        "Fried Rice Varities",   150,  "veg",     1),
    ("Mushroom Fried Rice",              "65",         "Fried Rice Varities",   130,  "veg",     1),
    ("Schezwan Mushroom Rice",           "551",        "Fried Rice Varities",   140,  "veg",     1),
    ("Egg Fried Rice",                   "109",        "Fried Rice Varities",   130,  "egg",     1),
    ("Schezwan Egg Fried Rice",          "110",        "Fried Rice Varities",   140,  "egg",     1),
    ("Chicken Fried Rice",               "111",        "Fried Rice Varities",   150,  "non-veg", 1),
    ("Schezwan Chicken Fried Rice",      "112",        "Fried Rice Varities",   160,  "non-veg", 1),
    ("Mixed Veg Fried Rice",             "333",        "Fried Rice Varities",     0,  "veg",     1),
    ("Mixed Non-Veg Fried Rice",         "503",        "Fried Rice Varities",     0,  "non-veg", 1),
    ("Kash Mivi Pulav",                  "560",        "Fried Rice Varities",   100,  "veg",     1),
    ("Prawn Fried Rice",                 "523",        "Fried Rice Varities",   170,  "veg",     1),
    ("Veg Noodles",                      "59",         "Noodles Varities",      110,  "veg",     1),
    ("Schezwan Veg Noodles",             "60",         "Noodles Varities",      120,  "veg",     1),
    ("Gobi Noodles",                     "576",        "Noodles Varities",      120,  "veg",     1),
    ("Schezwan Gobi Noodles",            "546",        "Noodles Varities",      130,  "veg",     1),
    ("Paneer Nooldes",                   "62",         "Noodles Varities",      140,  "veg",     1),
    ("Schezwan Paneer Noodles",          "548",        "Noodles Varities",      150,  "veg",     1),
    ("Mushroom Noodles",                 "61",         "Noodles Varities",      130,  "veg",     1),
    ("Schezwan Mushroom Nooldes",        "549",        "Noodles Varities",      140,  "veg",     1),
    ("Egg Noodles",                      "105",        "Noodles Varities",      130,  "egg",     1),
    ("Schezwan Egg Noodles",             "106",        "Noodles Varities",      140,  "egg",     1),
    ("Chicken Noodles",                  "107",        "Noodles Varities",      150,  "non-veg", 1),
    ("Schezwan Chicken Noodles",         "108",        "Noodles Varities",      160,  "non-veg", 1),
    ("Mixed Veg Noodles",                "519",        "Noodles Varities",        0,  "veg",     1),
    ("Mixed Non-Veg Noodles",            "518",        "Noodles Varities",        0,  "non-veg", 1),
    ("Prawn Noodles",                    "542",        "Noodles Varities",      170,  "veg",     1),
    ("Singapore Noodles",                "567",        "Noodles Varities",      100,  "veg",     1),
    ("Paneer Butter Masala",             "55",         "Veg Gravy Varities",    150,  "veg",     1),
    ("Mushroom Masala",                  "56",         "Veg Gravy Varities",    130,  "veg",     1),
    ("Gobi Masala",                      "307",        "Veg Gravy Varities",    140,  "veg",     1),
    ("Mixed Veg Gravy",                  "58",         "Veg Gravy Varities",    160,  "veg",     1),
    ("Malai Goftha",                     "565",        "Veg Gravy Varities",    100,  "veg",     1),
    ("Gobi Chilly",                      "44",         "Veg Dry Varities",       90,  "veg",     1),
    ("Gobi 65",                          "46",         "Veg Dry Varities",      100,  "veg",     1),
    ("Gobi Pepper Fry",                  "578",        "Veg Dry Varities",      130,  "veg",     1),
    ("Gobi Manchurian",                  "45",         "Veg Dry Varities",      140,  "veg",     1),
    ("Mushroom Chilly",                  "47",         "Veg Dry Varities",      100,  "veg",     1),
    ("Mushroom 65",                      "48",         "Veg Dry Varities",      140,  "veg",     1),
    ("Mushroom Pepper Fry",              "49",         "Veg Dry Varities",      140,  "veg",     1),
    ("Mushroom Manchurian",              "171",        "Veg Dry Varities",      150,  "veg",     1),
    ("Paneer Chilly",                    "50",         "Veg Dry Varities",      140,  "veg",     1),
    ("Paneer 65",                        "514",        "Veg Dry Varities",      150,  "veg",     1),
    ("Paneer Pepper Fry",                "488",        "Veg Dry Varities",      160,  "veg",     1),
    ("Paneer Manchurian",                "385",        "Veg Dry Varities",      170,  "veg",     1),
    ("Plain Gravy",                      "136",        "Non-veg Gravy Dishes",  100,  "non-veg", 1),
    ("Chettinad Chicken Gravy",          "465",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Pepper Chicken Gravy",             "466",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Butter Chicken Gravy",             "133",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Garlic Chicken Gravy",             "135",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Ginger Chicken Gravy",             "134",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Ginger Garlic Gravy",              "504",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Hyderabad Chicken Gravy",          "361",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Chicken Leg Piece Gravy",          "128",        "Non-veg Gravy Dishes",  250,  "non-veg", 1),
    ("Chilly Chicken Gravy",             "496",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Chicken Pallipalayam Gravy",       "571",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Chicken Sinthamani Gravy",         "572",        "Non-veg Gravy Dishes",    0,  "non-veg", 1),
    ("Chicken Gravy Bonless",            "464",        "Non-veg Gravy Dishes",  270,  "veg",     1),
    ("Chilli Bone",                      "305",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Chilli Boneless",                  "334",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Chicken Fry Bone [Half]",          "115",        "Non-veg Dry Dishes",    160,  "non-veg", 1),
    ("Chicken 65 [half]",                "310",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Chicken Pakkoda [Half]",           "118",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Chicken Manchurian [Half]",        "117",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Pepper Chicken Dry",               "474",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Hot Pepper Chicken [Half]",        "413",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Chicken Chukka [Half]",            "120",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Schezwan Chicken [Half]",          "335",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Hyderabad Chicken [Half]",         "573",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Chicken Pallipalayam [Half]",      "119",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Super Chicken [2 Pieces]",         "170",        "Non-veg Dry Dishes",    160,  "non-veg", 1),
    ("Nattukozhi Kulambu",               "147",        "Non-veg Dry Dishes",    240,  "non-veg", 1),
    ("Chicken Sintamani Dry [Half]",     "582",        "Non-veg Dry Dishes",      0,  "non-veg", 1),
    ("Chilly Bone (Half)",               "113",        "Non-veg Dry Dishes",    100,  "veg",     1),
    ("Chilly Boneless (Half)",           "114",        "Non-veg Dry Dishes",    180,  "veg",     1),
    ("Chicken Lollipop (2pcs)",          "481",        "Non-veg Dry Dishes",    100,  "non-veg", 1),
    ("Chicken Lollipop (4pcs)",          "126",        "Non-veg Dry Dishes",    200,  "non-veg", 1),
    ("Nattukozhi Fry",                   "146",        "Non-veg Dry Dishes",    240,  "non-veg", 1),
    ("Chicken Fry Bonless",              "123",        "Non-veg Dry Dishes",    170,  "veg",     1),
    ("Nattukozhi Pallipalayam",          "NCPA",       "Non-veg Dry Dishes",    300,  "non-veg", 1),
    ("Mutton Fry [half]",                "137",        "Mutton Dry Varities",   220,  "non-veg", 1),
    ("Mutton Chukka [half]",             "139",        "Mutton Dry Varities",   240,  "non-veg", 1),
    ("Mutton Masala [half]",             "144",        "Mutton Dry Varities",   260,  "non-veg", 1),
    ("Mutton Pallipalayam [half]",       "574",        "Mutton Dry Varities",   260,  "non-veg", 1),
    ("Kudal Fry [Half]",                 "141",        "Mutton Dry Varities",   160,  "non-veg", 1),
    ("Kudal Egg Fry [Half]",             "142",        "Mutton Dry Varities",   180,  "non-veg", 1),
    ("Kudal Masala [Half]",              "145",        "Mutton Dry Varities",   210,  "non-veg", 1),
    ("Kaadai Roast [1 Piece]",           "148",        "Kaadai Varities",       130,  "non-veg", 1),
    ("Kaadai Chilly",                    "152",        "Kaadai Varities",       140,  "non-veg", 1),
    ("Kaadai Fry",                       "150",        "Kaadai Varities",       160,  "non-veg", 1),
    ("Kaadai Masala",                    "149",        "Kaadai Varities",       210,  "non-veg", 1),
    ("Fish Kulambu",                     "420",        "Sea Food Varities",      70,  "non-veg", 1),
    ("Cutla Fish Roast [1 Piece]",       "155",        "Sea Food Varities",      60,  "non-veg", 1),
    ("Chilly Fish [12 Pieces]",          "156",        "Sea Food Varities",     160,  "non-veg", 1),
    ("Fish Finger 80Gms",                "352",        "Sea Food Varities",     160,  "non-veg", 1),
    ("Fish Cutlet [1 Piece]",            "440",        "Sea Food Varities",      50,  "non-veg", 1),
    ("Fish Manchurian",                  "353",        "Sea Food Varities",     170,  "non-veg", 1),
    ("Fish Masala",                      "306",        "Sea Food Varities",     180,  "non-veg", 1),
    ("Nethili Fish Chilly",              "437",        "Sea Food Varities",     170,  "non-veg", 1),
    ("Nethili Fish Masala",              "438",        "Sea Food Varities",     200,  "non-veg", 1),
    ("Nethilyi  Fish Pepper Fry",        "439",        "Sea Food Varities",     170,  "veg",     1),
    ("Prawn Chilly",                     "159",        "Sea Food Varities",     200,  "non-veg", 1),
    ("Prawn Pepper Fry",                 "158",        "Sea Food Varities",     210,  "non-veg", 1),
    ("Prawn Manchurian",                 "462",        "Sea Food Varities",     220,  "non-veg", 1),
    ("Prawn Masala",                     "168",        "Sea Food Varities",     260,  "non-veg", 1),
    ("Garlic Prawns",                    "463",        "Sea Food Varities",     250,  "non-veg", 1),
    ("Crab Lollipop [1 Piece]",          "436",        "Sea Food Varities",      50,  "non-veg", 1),
    ("Naan [1 Piece]",                   "34",         "Tandoori Bread Varities", 40, "veg",     1),
    ("Butter Naan [1 Piece]",            "35",         "Tandoori Bread Varities", 60, "veg",     1),
    ("Garlic Naan [1 Piece]",            "379",        "Tandoori Bread Varities", 70, "veg",     1),
    ("Roti [1 Piece]",                   "36",         "Tandoori Bread Varities", 40, "veg",     1),
    ("Butter Roti [1 Piece]",            "428",        "Tandoori Bread Varities", 60, "veg",     1),
    ("Grill Chicken",                    "412",        "Grill Items",             0,  "non-veg", 1),
    ("Grill Pepper Fry",                 "494",        "Grill Items",             0,  "veg",     1),
    ("Tandoori Chicken",                 "411",        "Tandoori Items",          0,  "non-veg", 1),
    ("Shawarma Roll",                    "441",        "Shawarma Varities",      100, "non-veg", 1),
    ("Shawarma Plate",                   "442",        "Shawarma Varities",      200, "non-veg", 1),
    ("Chocolate Lasagne [Online]",       "1 [Online]", "Desserts",              155,  "veg",     1),
    ("Misti Doi [Online]",               "2 [Online]", "Desserts",               60,  "veg",     1),
    ("Phirni [Online]",                  "3 [Online]", "Desserts",              120,  "veg",     1),
    ("Aam Panna [Online]",               "4 [Online]", "Beverages",              90,  "veg",     1),
    ("Kitkat Shake [Online]",            "5 [Online]", "Beverages",             155,  "veg",     1),
    ("Lemon Ice Tea [Online]",           "6 [Online]", "Beverages",              85,  "veg",     1),
    ("Mint Mojito [Online]",             "7 [Online]", "Beverages",             100,  "veg",     1),
    ("Soda Pet Bottle",                  "471",        "Beverages",              25,  "veg",     1),
    ("Coco Natta",                       "585",        "Beverages",              60,  "veg",     1),
    ("Container 500 Ml",                 "533",        "parcel",                  5,  "veg",     1),
    ("Container 250 Ml",                 "532",        "parcel",                  4,  "veg",     1),
    ("100ml Continer",                   "531",        "parcel",                  3,  "veg",     1),
    ("Jigerthanda",                      "556",        "parcel",                 75,  "veg",     1),
    ("Soda",                             "470",        "parcel",                 30,  "veg",     1),
    ("Mini Cool Drinks",                 "386",        "parcel",                 15,  "veg",     1),
    ("Water Bottel",                     "358",        "parcel",                 20,  "veg",     1),
    ("Pet Bottle",                       "777",        "parcel",                 30,  "veg",     1),
    ("Sprite 750 Ml",                    "454",        "parcel",                 40,  "veg",     1),
    ("Coke 750 Ml",                      "455",        "parcel",                 40,  "veg",     1),
    ("Mazza 750 Ml",                     "502",        "parcel",                 45,  "veg",     1),
    ("Water Bottel 2litter",             "359",        "parcel",                 30,  "veg",     1),
    ("Extra",                            "491",        "parcel",                  0,  "veg",     1),
]
# fmt: on


def _parse_short_code(raw: str) -> int | None:
    """Return int only if the string is a pure positive integer, else None."""
    try:
        val = int(raw.strip())
        return val if val > 0 else None
    except (ValueError, AttributeError):
        return None


def _parse_food_type(raw: str) -> str:
    raw = (raw or "").strip().lower()
    if "non" in raw:
        return "non_veg"
    if "egg" in raw:
        return "egg"
    return "veg"


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore[call-overload]

    async with async_session() as db:
        # Verify tenant exists
        row = (await db.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"),
            {"slug": SEED_TENANT_SLUG},
        )).first()
        if row is None:
            print(f"❌  Tenant '{SEED_TENANT_SLUG}' not found — run seed_super_admin.py first")
            return

        inserted = 0
        skipped = 0

        for (name, short_code_raw, category, price_rupees, food_type_raw, display_order) in MENU_ITEMS:
            # Idempotency: skip if (tenant_id, name, category) already exists
            existing = (await db.execute(
                text("SELECT id FROM menu_items WHERE tenant_id = :tid AND name = :name AND category = :cat"),
                {"tid": SEED_TENANT_SLUG, "name": name, "cat": category},
            )).first()
            if existing:
                skipped += 1
                continue

            short_code = _parse_short_code(short_code_raw)
            food_type = _parse_food_type(food_type_raw)
            price_paise = price_rupees * 100

            await db.execute(
                text("""
                    INSERT INTO menu_items
                        (tenant_id, name, category, short_code, price_paise,
                         food_type, is_available, display_order)
                    VALUES
                        (:tenant_id, :name, :category, :short_code, :price_paise,
                         CAST(:food_type AS food_type), true, :display_order)
                """),
                {
                    "tenant_id": SEED_TENANT_SLUG,
                    "name": name,
                    "category": category,
                    "short_code": short_code,
                    "price_paise": price_paise,
                    "food_type": food_type,
                    "display_order": display_order,
                },
            )
            inserted += 1

        await db.commit()
        print(f"✅  Seed complete — inserted: {inserted}, skipped (already exist): {skipped}")
        if inserted:
            print(f"\n   Run this to verify:")
            print(f"   SELECT category, count(*) FROM menu_items WHERE tenant_id = '{SEED_TENANT_SLUG}' GROUP BY 1 ORDER BY 1;")


if __name__ == "__main__":
    asyncio.run(seed())
