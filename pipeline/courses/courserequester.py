import requests
import time
import json
import re
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

headers = {"User-Agent": "LSU academic planner student project"}

EXTRA_IDS = [236832, 236845, 236908, 236916, 236929, 236933]

FULL_SWEEP = False

os.makedirs("raw/pages", exist_ok=True)

if FULL_SWEEP:
    coids = list(range(227992, 234500)) + EXTRA_IDS
else:
    coids = EXTRA_IDS

for coid in tqdm(coids):
    path = f"raw/pages/{coid}.html"
    if os.path.exists(path):
        continue

    url = f"https://catalog.lsu.edu/preview_course.php?catoid=35&coid={coid}&print"

    while True:
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.RequestException:
            tqdm.write(f"{coid} request failed, retrying in 1 min")
            time.sleep(60)
            continue

        if response.status_code == 202:
            tqdm.write(f"{coid} blocked, pausing 1 min...")
            time.sleep(60)
            continue

        break

    time.sleep(0.5)

    if response.status_code != 200:
        tqdm.write(f"{coid} bad status: {response.status_code}")
        continue

    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")

    if h1 is None:
        tqdm.write(f"{coid} Error: not a course page!!!!!")
        with open("bad.html", "w", encoding="utf-8") as f:
            f.write(html)
        continue

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


print(len(os.listdir("raw/pages")), "pages saved")