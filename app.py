from flask import Flask, render_template, request
from planner.rules import audit, GENED_SETS, check_total_hours, check_plan, courses, check_hours

import json

with open("data/degrees.json", "r", encoding="utf-8") as f:
    degrees = json.load(f)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    options = []
    plan_text = ""
    selected = ""
    prior_text = ""

    if request.method == "POST":
        selected = request.form["track"]
        prior_text = request.form.get("prior", "")
        poid, index = selected.split("|")
        track = degrees[poid]["tracks"][int(index)]

        lines = []
        seen_groups = set()

        for semester in track["semesters"]:
            codes = []
            skip_next = False

            for item in semester["items"]:
                if item["type"] != "course":
                    continue

                if skip_next:
                    skip_next = False
                    continue

                group = item.get("group")
                if group is not None:
                    if group in seen_groups:
                        continue
                    seen_groups.add(group)

                codes.append(item["code"])

                if item["connector"] == "or":
                    skip_next = True

            lines.append(",".join(codes))

        plan_text = "\n".join(lines)

    for poid, program in degrees.items():
        for i, track in enumerate(program["tracks"]):
            value = f"{poid}|{i}"

            if track["name"] == program["title"]:
                label = program["title"]
            else:
                label = f"{program['title']} - {track['name']}"

            options.append({"value": value, "label": label})

    options.sort(key=lambda o: o["label"])
    return render_template("home.html", options=options, plan_text=plan_text, selected=selected, prior_text=prior_text)


@app.route("/audit", methods=["POST"])
def audit_page():
    choice = request.form["track"]
    poid, index = choice.split("|")

    track = degrees[poid]["tracks"][int(index)]

    text = request.form["plan"]
    plan = []

    prior_raw = request.form.get("prior", "")
    prior_raw = prior_raw.replace("\n", ",")

    prior = {piece.strip().upper() for piece in prior_raw.split(",") if piece.strip()}

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        semester = [piece.strip().upper() for piece in line.split(",") if piece.strip()]
        plan.append(semester)

    report = audit(plan, prior, track, GENED_SETS)
    rows = []

    for r in report["results"]:
        req = r["requirement"]

        if req["type"] == "course":
            label = " or ".join(req["options"])
            if r["filled_by"] is not None:
                mark = "✓"
            else:
                mark = "✗"
        else:
            label = req["slot"]["description"]
            if r["hours"] >= r["needed"]:
                mark = "✓"
            elif r["filled_by"]:
                mark = "◐"
            else:
                mark = "✗"

        if not r["filled_by"]:
            filled = "-"
        elif isinstance(r["filled_by"], list):
            filled = ", ".join(r["filled_by"])
        else:
            filled = r["filled_by"]

        rows.append({"mark": mark, "label": label, "filled_by": filled})

    prereq_problems = check_plan(plan, prior, courses)
    hours = check_hours(plan, courses, max_hours=19, approved_max=21, min_hours=12)
    total = check_total_hours(plan, prior, track)

    return render_template("audit.html", results=rows, prereq_problems=prereq_problems, hours=hours, total=total)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
