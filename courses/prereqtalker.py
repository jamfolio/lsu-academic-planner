import ollama
import json
import re
import os
from tqdm import tqdm

instructions = """Convert course prerequisite text into JSON rules.
   Allowed forms:
    - {"course": "MATH 1550"}
    - {"course": "PHYS 2110", "concurrent": true}   (for "credit or registration in")
    - {"consent": "instructor"} or {"consent": "department"}
    - {"equivalent": true}   (for "or equivalent")
    - {"other": "text"}   (any requirement that is not a course, e.g. "majors only")
    - {"and": [ ... ]} and {"or": [ ... ]}   (can be nested)
    - {"consent": "college"}

    Only use course codes that appear in the text. Output only the JSON, nothing else.

    Examples:
    Text: MATH 1552 or MATH 1553.
    JSON: {"or": [{"course": "MATH 1552"}, {"course": "MATH 1553"}]}

    Text: ART 1360 and permission of instructor.
    JSON: {"and": [{"course": "ART 1360"}, {"consent": "instructor"}]}

    Text: MATH 1550 and credit or registration in PHYS 2110.
    JSON: {"and": [{"course": "MATH 1550"}, {"course": "PHYS 2110", "concurrent": true}]}

    Text: ANSC 1011 and CHEM 2060 or equivalent.
    JSON: {"and": [{"course": "ANSC 1011"}, {"or": [{"course": "CHEM 2060"}, {"equivalent": true}]}]}

    Text: Permission of College.
    JSON: {"consent": "college"}

   Now convert this:
   Text: """

with open("courses/courseswithrules.json", "r", encoding="utf-8") as f:
    courses = json.load(f)

if os.path.exists("courses/llmrules.json"):
    with open("courses/llmrules.json", "r", encoding="utf-8") as f:
        results = json.load(f)
else:
    results = {}

todo = []

for code, course in courses.items():
    rule = course["prereq_rule"]

    if rule is None or not rule.get("needs_review"):
        continue

    if code in results:
        continue

    todo.append((code, course))

for code, course in tqdm(todo):
    prompt = instructions + course["prereq"] + "\nJSON:"

    response = ollama.chat(
        model="gemma4:12b",
        messages=[{"role": "user", "content": prompt}],
        format="json",
        think=False,
    )

    reply = response["message"]["content"]

    try:
        new_rule = json.loads(reply)
    except json.JSONDecodeError:
        tqdm.write(f"{code} failed")
        continue

    rule_codes = re.findall(r"[A-Z]+ \d{4}", json.dumps(new_rule))
    valid = True

    for c in rule_codes:
        if c not in course["prereq"] or c not in courses:
            tqdm.write(f"{code} bad code: {c}")
            valid = False

    if not valid:
        continue

    new_rule["source"] = "llm"
    results[code] = new_rule

    if len(results) % 25 == 0:
        with open("courses/llmrules.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

with open("courses/llmrules.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

print(len(results))