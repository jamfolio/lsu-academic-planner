from bs4 import BeautifulSoup
import re
import os
import json

degree_programs = {}

os.makedirs("degree_programs", exist_ok=True)

for filename in ["14178.html"]:
    if not filename.endswith(".html"):
        continue

    with open (f"programs/{filename}", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all("div", class_="acalog-core")

    for block in divs:
        heading = block.find(["h2", "h3", "h4", "h5", "h6"])

        if heading is None:
            continue

        print(f"{heading.get_text(strip=True)}")

        items = block.find_all("li")

        for item in items:
            classes = item.get("class") or []
            text = item.get_text(" ", strip=True)
            # print("  ", item.get("class"), item.get_text(" ", strip=True))
            if "acalog-course" in classes:
                print("COURSE", text)
                # code = re.match(r"[A-Z]+\s+\d{4}", text)
                # credits = re.search(r"\((.*?)\)", text)
                or_ending = text.endswith(" or")
                and_ending = text.endswith(" and")
            elif "acalog-adhoc-list-item" in classes:
                print("SLOT", text)
            elif "acalog-adhoc" in classes:
                if not text:
                    print("SPACER")
                elif text.startswith("CRITICAL"):
                    print("CRITICAL", text)
                else:
                    print("NOTE", text)
            else:
                print("UNKNOWN", text)


