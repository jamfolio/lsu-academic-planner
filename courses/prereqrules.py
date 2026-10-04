import re
import os
import json


def parse_prereq(text):
    extras = []
    required = []
    text = text.rstrip(".")

    ending = re.search(
        r" or (?:consent|permission) of (?:the )?(instructor|department)$", text.lower()
    )

    if ending is not None:
        extras.append({"consent": ending.group(1)})
        text = text[: ending.start()]

    permission = re.search(
        r",? and (?:consent|permission) of (?:the )?(instructor|department)$",
        text.lower(),
    )

    if permission is not None:
        required.append({"consent": permission.group(1)})
        text = text[: permission.start()]

    reg = re.search(r"credit or registration in ([A-Z]+ \d{4})$", text, re.IGNORECASE)

    if reg is not None:
        required.append({"course": reg.group(1), "concurrent": True})
        text = text[: reg.start()]
        text = re.sub(r",?\s*(and)?\s*$", "", text)

    if text.endswith("or equivalent"):
        extras.append({"equivalent": True})
        text = text[: -len(" or equivalent")]

    core = None

    match = re.fullmatch(r"([A-Z]+ \d{4})", text)
    any_of = re.fullmatch(r"[A-Z]+ \d{4}( or [A-Z]+ \d{4})+", text)
    all_of = re.fullmatch(r"[A-Z]+ \d{4}(?:(?:, and |, | and )[A-Z]+ \d{4})+", text)
    codes = re.findall(r"([A-Z]+ \d{4})", text)
    whole = re.fullmatch(
        r"(?:consent|permission) of (?:the )?(instructor|department)", text.lower()
    )

    if whole:
        core = {"consent": whole.group(1)}
    elif match:
        core = {"course": match.group(1)}
    elif any_of:
        core = {"or": [{"course": c} for c in codes]}
    elif all_of:
        core = {"and": [{"course": c} for c in codes]}
    elif text == "" and required:
        core = required.pop(0)

    if core is None:
        return None

    if required:
        core = {"and": [core] + required}

    if extras:
        return {"or": [core] + extras}

    return core


with open("courses/courses.json", "r", encoding="utf-8") as f:
    courses = json.load(f)

total_prereqs = 0
handled = 0

for code, course in courses.items():
    course["prereq_rule"] = None

    if course["prereq"] is None:
        continue

    prereq_text = course["prereq"]
    total_prereqs = total_prereqs + 1

    rule = parse_prereq(prereq_text)

    if rule is not None:
        handled = handled + 1
    else:
        rule = {
            "needs_review": True,
            "text": prereq_text,
            "courses": re.findall(r"[A-Z]+ \d{4}", prereq_text),
        }
    
    course["prereq_rule"] = rule

with open("courses/courseswithrules.json", "w", encoding="utf-8") as f:
    json.dump(courses, f, ensure_ascii=False, indent=2)

print(handled, "of", total_prereqs)
