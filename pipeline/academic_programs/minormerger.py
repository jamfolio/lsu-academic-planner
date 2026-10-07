import json

with open("pipeline/academic_programs/minors.json", "r", encoding="utf-8") as f:
    minors = json.load(f)

with open("pipeline/academic_programs/minorrules.json", "r", encoding="utf-8") as f:
    minor_rules = json.load(f)

with open("pipeline/academic_programs/manualminorfixes.json", "r", encoding="utf-8") as f:
    manual_minors = json.load(f)

missing = 0

for title, minor in minors.items():
    if title in manual_minors:
        rule = manual_minors[title]
    else:
        rule = minor_rules.get(title)

    minor["rule"] = rule

    if minor["rule"] is None:
        missing += 1

print(missing)

with open("data/minorsfinal.json", "w", encoding="utf-8") as f:
    json.dump(minors, f, ensure_ascii=False, indent=2)
