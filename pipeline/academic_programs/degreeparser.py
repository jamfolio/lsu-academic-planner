from bs4 import BeautifulSoup
import re
import os
import json

PROGRAMS_FOLDER = "raw/programs"
OUTPUT_FILE = "data/degrees.json"

FOOTNOTE_START = re.compile(r"^(\d+)\s*[–-]\s*(.*)")

degree_programs = {}

for filename in os.listdir(PROGRAMS_FOLDER):
    if not filename.endswith(".html"):
        continue

    with open(os.path.join(PROGRAMS_FOLDER, filename), "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all("div", class_="acalog-core")
    h1 = soup.find("h1")

    title = h1.get_text(strip=True)

    program = {"title": title, "tracks": [], "notes": []}

    current = None
    current_track = None
    last_fn = None
    last_heading = None
    last_number = None
    group_id = 0

    for block in divs:
        heading = block.find(["h2", "h3", "h4", "h5", "h6"])

        if heading is None:
            continue

        heading_text = heading.get_text(" ", strip=True).replace("\xa0", " ")

        if heading_text.startswith("Semester"):
            number = re.search(r"\d+", heading_text)
            if number is not None:
                number = int(number.group(0))

            if current_track is None or (
                number is not None and last_number is not None and number <= last_number
            ):
                track = {
                    "name": last_heading or title,
                    "total_hours": None,
                    "semesters": [],
                    "footnotes": {},
                    "notes": [],
                }
                program["tracks"].append(track)
                current_track = track

            semester = {
                "name": heading_text,
                "hours": None,
                "critical": [],
                "items": [],
            }

            current_track["semesters"].append(semester)
            current = semester
            last_number = number
            last_fn = None

        elif re.match(r"^\d+\s+Total Sem", heading_text):
            total_hours = re.search(r"[\d-]+", heading_text)

            if current_track is not None:
                current_track["total_hours"] = total_hours.group(0)

        elif heading_text.startswith("Total Semester Hours"):
            hours = re.search(r"[\d-]+", heading_text)

            if current is not None and hours is not None:
                current["hours"] = hours.group(0)

        else:
            if heading_text not in (
                "Critical Requirements",
                "Prerequisite Courses:",
                "Notes:",
                "Note:",
                "Required For Bachelor’s Degree:",
            ):
                last_heading = heading_text

        if heading_text.startswith("Semester"):
            items = block.find_all("li")
        else:
            items = []

        current_group = None

        for item in items:
            if current is None:
                continue

            footnote = None
            for sup in item.find_all("sup"):
                number_text = sup.get_text(strip=True)
                if number_text:
                    footnote = number_text
                sup.extract()

            classes = item.get("class") or []
            text = item.get_text(" ", strip=True).replace("\xa0", " ")

            if "acalog-course" not in classes and re.search(
                r"(choose|select)\s+(one|1)\b.*following", text, re.IGNORECASE
            ):
                group_id += 1
                current_group = group_id
                continue

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
                        "footnote": footnote,
                        "group": current_group,
                    }
                )

            elif "acalog-adhoc" in classes and "acalog-adhoc-list-item" not in classes:
                current_group = None

                if not text:
                    pass

                elif re.match(r"critical\b", text, re.IGNORECASE):
                    current["critical"].append(
                        re.sub(r"^critical\s*:?\s*", "", text, flags=re.IGNORECASE)
                    )

                elif re.search(r"\(\d+(?:-\d+)?\)", text):
                    found = re.findall(r"\((\d+(?:-\d+)?)\)", text)
                    current["items"].append(
                        {
                            "type": "slot",
                            "credits": found[0],
                            "allowed_courses": re.findall(r"[A-Z]+ \d{4}", text),
                            "description": text,
                            "footnote": footnote,
                        }
                    )

                else:
                    print("NOTE", text)

            else:
                if not text:
                    continue

                if re.match(r"critical\b", text, re.IGNORECASE):
                    current["critical"].append(
                        re.sub(r"^critical\s*:?\s*", "", text, flags=re.IGNORECASE)
                    )
                    continue

                if "acalog-adhoc-before" not in classes:
                    current_group = None

                found = re.findall(r"\((.*?)\)", text)
                if found:
                    credits = found[-1]
                else:
                    credits = None

                allowed_courses = re.findall(r"[A-Z]+ \d{4}", text)

                current["items"].append(
                    {
                        "type": "slot",
                        "credits": credits,
                        "allowed_courses": allowed_courses,
                        "description": text,
                        "footnote": footnote,
                        "group": current_group,
                    }
                )

        for p in block.find_all("p"):
            text = p.get_text(" ", strip=True).replace("\xa0", " ")
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r" ([.,;:])", r"\1", text)

            if not text or text.startswith(("CRITICAL", "SEMESTER")):
                continue

            target = current_track if current_track is not None else program

            m = FOOTNOTE_START.match(text)

            if m and current_track is not None:
                last_fn = m.group(1)
                current_track["footnotes"][last_fn] = m.group(2)

            elif last_fn is not None and current_track is not None:
                current_track["footnotes"][last_fn] += " " + text

            else:
                target["notes"].append(text)

    program["footnotes"] = {}

    for p in soup.find_all("p"):
        if p.find("sup") is None:
            continue

        number = None
        for child in p.descendants:
            if getattr(child, "name", None) == "sup":
                sup_text = child.get_text(strip=True)
                if sup_text.isdigit():
                    number = sup_text
                    program["footnotes"][number] = ""
                continue

            if isinstance(child, str) and number is not None:
                if child.parent.name == "sup":
                    continue
                program["footnotes"][number] += child

    for number, text in program["footnotes"].items():
        text = re.sub(r"\s+", " ", text.replace("\xa0", " "))
        text = re.sub(r" ([.,;:])", r"\1", text)
        program["footnotes"][number] = text.strip().lstrip("–-").strip()

    if len(program["tracks"]) == 1:
        program["tracks"][0]["name"] = title

    if program["tracks"]:
        degree_programs[filename[:-5]] = program


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(degree_programs, f, ensure_ascii=False, indent=2)

print(len(degree_programs))
