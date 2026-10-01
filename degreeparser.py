from bs4 import BeautifulSoup
import re
import os
import json

degree_programs = {}

os.makedirs("degree_programs", exist_ok=True)

for filename in os.listdir("programs"):
    if not filename.endswith(".html"):
        continue

    with open(f"programs/{filename}", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all("div", class_="acalog-core")
    h1 = soup.find("h1")

    title = h1.get_text(strip=True)

    program = {"title": title, "total_hours": None, "semesters": []}

    current = None

    for block in divs:
        heading = block.find(["h2", "h3", "h4", "h5", "h6"])

        if heading is None:
            continue

        heading_text = heading.get_text(strip=True)

        if heading_text.startswith("Semester"):
            semester = {
                "name": heading_text,
                "hours": None,
                "critical": [],
                "items": [],
            }

            program["semesters"].append(semester)
            current = semester

        elif heading_text.startswith("Total Semester Hours"):
            hours = re.search(r"[\d-]+", heading_text)
            
            if current is not None:
                current["hours"] = hours.group(0)

        elif "Total Sem. Hrs." in heading_text:
            total_hours = re.search(r"[\d-]+", heading_text)
            program["total_hours"] = total_hours.group(0)

        items = block.find_all("li")

        for item in items:
            if current is None:
                continue

            classes = item.get("class") or []
            text = item.get_text(" ", strip=True)

            if "acalog-course" in classes:
                code = re.match(r"[A-Z]+ \d{4}", text)
                if code is None:
                    continue
                else:
                    code = code.group(0)

                found = re.findall(r"\((.*?)\)", text)
                if found:
                    credits = found[-1]
                else:
                    credits = None

                if text.endswith(" or"):
                    connector = "or"

                elif text.endswith(" and"):
                    connector = "and"

                else:
                    connector = None

                current["items"].append(
                    {
                        "type": "course",
                        "code": code,
                        "credits": credits,
                        "connector": connector,
                    }
                )

            elif "acalog-adhoc-list-item" in classes:
                found = re.findall(r"\((.*?)\)", text)
                if found:
                    credits = found[-1]
                else:
                    credits = None

                allowed_courses = re.findall(r"[A-Z]+ \d{4}", text)

                description = text

                current["items"].append(
                    {
                        "type": "slot",
                        "credits": credits,
                        "allowed_courses": allowed_courses,
                        "description": description,
                    }
                )

            elif "acalog-adhoc" in classes:
                if not text:
                    pass

                elif text.startswith("CRITICAL"):
                    current["critical"].append(re.sub(r"^CRITICAL\s*:\s*", "", text))

                else:
                    print("NOTE", text)

            else:
                print("UNKNOWN", text)

    if program["semesters"]:
        degree_programs[filename[:-5]] = program


with open("degree_programs/degrees.json", "w", encoding="utf-8") as f:
    json.dump(degree_programs, f, ensure_ascii=False, indent=2)

print(len(degree_programs))
