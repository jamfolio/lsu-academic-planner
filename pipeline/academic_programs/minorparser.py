from bs4 import BeautifulSoup
import re
import os
import json

minors = {}

os.makedirs("academic_programs", exist_ok=True)

for filename in os.listdir("programs"):
    if not filename.endswith(".html"):
        continue

    with open(f"programs/{filename}", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")

    title = h1.get_text(strip=True)

    if "Minor" not in title:
        continue

    div = soup.find("div", class_="program_description")

    if div is None:
        continue

    text = div.get_text(" ", strip=True)
    text = re.sub(r" ([.,;:])", r"\1", text)

    courses = re.findall(r"[A-Z]+ \d{4}", text)

    match = re.search(r"(\d+) (?:credit |semester )?hours", text)

    if match is None:
        total_hours = None
    else:
        total_hours = match.group(1)

    match = re.search(r"not available to [^.]*\.", text)

    if match is None:
        not_available_to = None
    else:
        not_available_to = match.group(0)

    minors[filename[:-5]] = {
        "title": title,
        "text": text,
        "courses": courses,
        "total_hours": total_hours,
        "not_available_to": not_available_to,
    }

with open("academic_programs/minors.json", "w", encoding="utf-8") as f:
    json.dump(minors, f, ensure_ascii=False, indent=2)

print(len(minors))
