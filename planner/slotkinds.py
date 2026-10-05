import json
import re
from rules import classify_slot

with open("data/degrees.json", "r", encoding="utf-8") as f:
    degrees = json.load(f)

descriptions = set()

for poid, program in degrees.items():
    for track in program["tracks"]:
        for semester in track["semesters"]:
            for item in semester["items"]:
                if item["type"] == "slot":
                    desc = item["description"]
                    desc = desc.replace("\xa0", " ")
                    desc = re.sub(r"[\s\d,]+$", "", desc)
                    desc = re.sub(r"\s*\(\d+\)", "", desc)
                    desc = desc.strip()

                    descriptions.add(desc)

# print(len(descriptions))

# for desc in sorted(descriptions):
#     print(desc)

counts = {}

for desc in sorted(descriptions):
    result = classify_slot(desc)
    kind = result["kind"]
    counts[kind] = counts.get(kind, 0) + 1

print(counts)

for desc in sorted(descriptions):
    result = classify_slot(desc)
    if result["kind"] == "list" or result["kind"] == "subject":
        print(result["kind"], result, desc)

with open("data/geneds.json", "r", encoding="utf-8") as f:
    gen_eds = json.load(f)

for category, info in gen_eds.items():
    print(category)
    print(len(info["courses"]))
