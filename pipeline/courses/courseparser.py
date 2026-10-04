from bs4 import BeautifulSoup
import re
import os
import json

courses = {}

os.makedirs("courses", exist_ok=True)

for filename in os.listdir("pages"):
    if not filename.endswith(".html"):
        continue

    with open(f"pages/{filename}", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")

    title = h1.get_text(strip=True)
    match = re.match(r"^([A-Z]+\s+\d{4})\s+(.*?)(?:\s*\((.*?)\))?$", title)

    if match is None:
        continue
    else:
        code = match.group(1)
        title = match.group(2)
        credits = match.group(3)

    deciders = []
    stuff = []

    seen_hr = False

    for sibling in h1.next_siblings:
        if sibling.name == "hr":
            if seen_hr:
                break
            seen_hr = True
            continue

        text = sibling.get_text(" ", strip=True)
        text = re.sub(r" ([.,;:])", r"\1", text)

        if not text:
            continue

        if sibling.name in ("em", "i", "strong"):
            deciders.append(text)
        elif deciders and deciders[-1].endswith(":"):
            deciders.append(text)
        else:
            stuff.append(text)

    prereq = None
    coreq = None
    equivalents = []
    credit_rest = []
    repeat = []
    other = []

    next_is_prereq = False
    next_is_coreq = False

    for note in deciders:
        if (
            next_is_prereq
            and prereq is not None
            and not re.match(r"^([a-z.,;]|[A-Z]+ \d{4})", note)
        ):
            next_is_prereq = False

        if next_is_prereq:
            if prereq is None:
                prereq = note
            else:
                prereq = prereq + " " + note

            prereq = re.sub(r" ([.,;:])", r"\1", prereq)

            if prereq.endswith("."):
                next_is_prereq = False

        elif note.startswith("Prereq"):
            next_is_prereq = True

        elif next_is_coreq:
            coreq = note
            next_is_coreq = False

        elif note.startswith("Coreq"):
            next_is_coreq = True

        elif note.startswith(
            (
                "Same as",
                "Also offered as",
                "See ",
                "See:",
                "An honors course",
                "An Honors course",
            )
        ):
            equivalents.append(note)

        elif note.startswith("Credit will"):
            credit_rest.append(note)

        elif note.startswith(("May be taken", "May be repeated")):
            repeat.append(note)

        else:
            other.append(note)

    if prereq is not None:
        credit_rest.extend(re.findall(r"Credit will[^.]*\.", prereq))
        equivalents.extend(re.findall(r"An [Hh]onors course[^.]*\.", prereq))

        prereq = re.sub(r"Credit will[^.]*\.", "", prereq)
        prereq = re.sub(r"An [Hh]onors course[^.]*\.", "", prereq)
        prereq = prereq.strip() or None

    description = " ".join(stuff)
    description = re.sub(r" ([.,;:])", r"\1", description)
    description = description.lstrip(" .,;")

    credit_rest.extend(re.findall(r"Credit will[^.]*\.", description))
    equivalents.extend(re.findall(r"An [Hh]onors course[^.]*\.", description))

    description = re.sub(r"Credit will[^.]*\.", "", description)
    description = re.sub(r"An [Hh]onors course[^.]*\.", "", description)
    description = description.strip()

    if code not in courses or (
        courses[code]["credits"] is None and credits is not None
    ):
        courses[code] = {
            "code": code,
            "title": title,
            "credits": credits,
            "prereq": prereq,
            "coreq": coreq,
            "equivalent_courses": equivalents,
            "restricted_credits": credit_rest,
            "repeatable": repeat,
            "other": other,
            "description": description,
        }

with open("courses/courses.json", "w", encoding="utf-8") as f:
    json.dump(courses, f, ensure_ascii=False, indent=2)

print(len(courses))
