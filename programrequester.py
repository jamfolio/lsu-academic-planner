import requests
import time
import json
import re
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

from seleniumbase import Driver

# headers = {"User-Agent": "LSU academic planner student project"}
driver = Driver(uc=False)

os.makedirs("programs", exist_ok=True)

# driver.quit()

for poid in tqdm(range(14104, 14638)):
    path = f"programs/{poid}.html"
    if os.path.exists(path):
        continue

    url = f"https://catalog.lsu.edu/preview_program.php?catoid=35&poid={poid}"

    while True:
        try:
            driver.get(url)
            # driver.page_source
            # response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        except requests.RequestException:
            tqdm.write(f"{poid} request failed, retrying in 1 min")
            time.sleep(60)
            continue

        # if response.status_code == 202:
            # tqdm.write(f"{poid} blocked, pausing for 1 min...")
            # time.sleep(60)
            # continue

        break

    time.sleep(3)

    # if response.status_code != 200:
        # tqdm.write(f"{poid} bad status: {response.status_code}")
        # continue

    # html = response.text
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
