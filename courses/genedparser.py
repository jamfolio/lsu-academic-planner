from bs4 import BeautifulSoup
import re
import os
import json

gen_eds = {}

os.makedirs("courses", exist_ok=True)

for filename in [
    "14233.html",
    "14234.html",
    "14235.html",
    "14236.html",
    "14237.html",
    "14238.html",
]:
    if not filename.endswith(".html"):
        continue

    with open(f"programs/{filename}", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")

    title = h1.get_text(strip=True)
    match = re.match(r"^[IVX]+\.\s*(.*?)\s*\((\d+) Sem\. Hrs\.\)", title)

    if match is None:
        continue
    else:
        category = match.group(1)
        hours = match.group(2)

    courses = soup.find_all("li", class_="acalog-course")
    codes = []

    for code in courses:
        code = code.get_text(strip=True)
        code = re.search(r"[A-Z]+ \d{4}", code)

        if code is not None:
            codes.append(code.group(0))

    gen_eds[category] = {"hours": hours, "courses": codes}

with open("courses/gen_eds.json", "w", encoding="utf-8") as f:
    json.dump(gen_eds, f, ensure_ascii=False, indent=2)
