import json

def recommended_plan(track):
    semesters = []
    seen_groups = set()

    for semester in track["semesters"]:
        items = []
        skip_next = False

        for item in semester["items"]:
            if item["type"] == "slot":
                if item.get("group") is not None:
                    continue
                else:
                    items.append(
                        {
                            "type": "slot",
                            "description": item["description"],
                            "credits": item["credits"],
                        }
                    )
                    continue
            
            if skip_next:
                skip_next = False
                continue
            group = item.get("group")
            if group is not None:
                if group in seen_groups:
                    continue
                seen_groups.add(group)

            items.append({"type": "course", "code": item["code"]})

            if item["connector"] == "or":
                skip_next = True
        semesters.append(items)
    return semesters

if __name__ == "__main__":
    with open("data/degrees.json", "r", encoding="utf-8") as f:
        degrees = json.load(f)

    track = degrees["14278"]["tracks"][4]

    for semester in recommended_plan(track):
        print(semester)