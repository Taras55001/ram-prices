import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

products = {
    "Gskill_DDR4_16GB": {
        "name": "G.Skill Aegis 16GB DDR4",
        "urls": [
            "https://azerty.nl/product/g-skill-ripjaws-v-f4-3600c18d-16gvk-geheugen/4250899",
            "https://www.amazon.com.be/-/en/G-Skill-Ripjaws-32GVKC-2x16GB-F4-3600C16D-32GVKC/dp/B07Z86BMCQ/"
        ]
    },
    "Corsair_DDR5_32GB": {
        "name": "Corsair Vengeance DDR5 32GB",
        "urls": [
            "https://azerty.nl/product/corsair-vengeance-geheugen/5573534",
            "https://www.amazon.com.be/-/en/CORSAIR-Vengeance-6000MHz-Compatible-Computer/dp/B0CBRJ63RT/?th=1"
        ]
    },
    "Kingston_DDR5_5600": {
        "name": "Kingston FURY Beast DDR5",
        "urls": [
            "https://azerty.nl/product/kingston-fury-beast-black-geheugen/4983206",
            "https://www.amazon.com.be/-/en/Kingston-Beast-2x16GB-5600MT-Memory/dp/B0BD5PN65B/"
        ]
    }
}

def fetch_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    resp = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    price_text = None

    if "amazon" in url:
        tag = soup.select_one("span.a-offscreen")
        if tag:
            price_text = tag.get_text(strip=True)

    if "azerty.nl" in url:
        tag = soup.select_one("span.price span.price")
        if not tag or not tag.contents:
            return None

        price_text = tag.contents[0]
        price_text = price_text.replace(",-", ".00").replace(",", ".")

        return float(price_text)

    if not price_text:
        return None

    # Виймаємо число типу 149,99 або 149.99
    match = re.search(r"[\d,.]+", price_text)
    if not match:
        return None



CSV_FILE = "ram_prices.csv"

if os.path.exists(CSV_FILE):
    df_history = pd.read_csv(CSV_FILE, parse_dates=["datetime"])
else:
    df_history = pd.DataFrame(columns=["datetime", "product_id", "store", "price"])
new_data = []

for pid, meta in products.items():
    for url in meta["urls"]:
        price = fetch_price(url)
        if price:
            new_data.append({
                "datetime": datetime.now(),
                "product_id": pid,
                "store": url.split("/")[2],
                "price": price
            })
df_new = pd.DataFrame(new_data)
df_all = pd.concat([df_history, df_new], ignore_index=True)
df_all.to_csv(CSV_FILE, index=False)
