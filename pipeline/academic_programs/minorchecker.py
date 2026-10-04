import json
import re

with open("academic_programs/minorrules.json", "r", encoding="utf-8") as f:
    minor_rules = json.load(f)

bad = set()

for key, rule in minor_rules.items():
    dumped = json.dumps(rule)

    course_value = re.findall(r'"course": "([^"]*)"', dumped)

    for value in course_value:
        if not re.fullmatch(r"[A-Z]{2,5} \d{4}", value):
            print(f"{key}: {value}")
            bad.add(key)

    pieces = re.findall(r'"courses": \[([^\]]*)\]', dumped)

    for piece in pieces:
        quoted = re.findall(r'"([^"]*)"', piece)

        for item in quoted:

            if not re.fullmatch(r"[A-Z]{2,5} \d{4}", item):
                print(f"{key}: {item}")
                bad.add(key)

for key in bad:
    del minor_rules[key]

with open("academic_programs/minorrules.json", "w", encoding="utf-8") as f:
    json.dump(minor_rules, f, ensure_ascii=False, indent=2)

print(len(bad))
