import json

with open("courses/courseswithrules.json", "r", encoding="utf-8") as f:
    course_rules = json.load(f)

with open("courses/llmrules.json", "r", encoding="utf-8") as f:
    llm_rules = json.load(f)

with open("courses/manualprereqfixes.json", "r", encoding="utf-8") as f:
    manual_fixes = json.load(f)

bad = {
    "GEOL 3666",
    "LHRD 7203",
    "HORT 2070",
    "RNR 4107",
    "PETE 4320",
    "FIN 7709",
    "LHRD 7731",
    "LHRD 7733",
    "LHRD 2002",
    "BIOL 4596",
    "CE 4760",
    "BIOL 4450",
    "BE 4310",
    "AGEC 3003",
    "PADM 7917",
    "CHEM 4564",
    "CHEM 4556",
    "MUS 2622",
    "PSYC 7979",
}

prereqs_merged = 0

for code, rule in llm_rules.items():
    if code in bad:
        continue

    if code not in course_rules:
        continue

    course_rules[code]["prereq_rule"] = rule

    prereqs_merged += 1

for code, rule in manual_fixes.items():
    if code not in course_rules:
        print(f"Warning! {code} is not in the course rules.")
        continue

    course_rules[code]["prereq_rule"] = rule

with open("courses/coursesfinal.json", "w", encoding="utf-8") as f:
    json.dump(course_rules, f, ensure_ascii=False, indent=2)

print(prereqs_merged)

needs_review = 0

for code, course in course_rules.items():
    rule = course["prereq_rule"]

    if rule is not None and rule.get("needs_review"):
        needs_review += 1
        print(f"{code}: {rule['text']}")

print(needs_review)
