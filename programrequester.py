import requests
import time
import json
import re
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

from seleniumbase import Driver

driver = Driver(uc=False)

os.makedirs("programs", exist_ok=True)

for poid in tqdm(range(14104, 14638)):
    path = f"programs/{poid}.html"
    if os.path.exists(path):
        continue

    url = f"https://catalog.lsu.edu/preview_program.php?catoid=35&poid={poid}"

    while True:
        try:
            driver.get(url)

        except requests.RequestException:
            tqdm.write(f"{poid} request failed, retrying in 1 min")
            time.sleep(60)
            continue

        break

    time.sleep(3)

    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")

    if h1 is None: 
        tqdm.write(f"{poid} Error: not a program page!!!!!")
        with open("bad.html", "w", encoding="utf-8") as f:
            f.write(html)
        continue

    with open(path, "w", encoding="utf-8") as f:
          f.write(html)


print(len(os.listdir("programs")), "programs saved")
