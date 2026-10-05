from flask import Flask, render_template, request
from planner.rules import (
    audit,
    GENED_SETS,
    check_total_hours,
    check_plan,
    courses,
    check_hours,
    is_satisfied,
)

import json

with open("data/degrees.json", "r", encoding="utf-8") as f:
    degrees = json.load(f)

with open("data/minorsfinal.json", "r", encoding="utf-8") as f:
    minors = json.load(f)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    options = []
    minor_options = []
    plan_text = ""
    selected_majors = ["", "", ""]
    selected_minors = ["", "", ""]
    prior_text = ""

    if request.method == "POST":
        selected_majors = request.form.getlist("major")
        selected_minors = request.form.getlist("minor")
        prior_text = request.form.get("prior", "")
        poid, index = selected_majors[0].split("|")
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

            if track["name"] in program["title"]:
                label = program["title"]
            else:
                label = f"{program['title']} - {track['name']}"

            options.append({"value": value, "label": label})

    for poid, minor in minors.items():
        minor_options.append({"value": poid, "label": minor["title"]})

    options.sort(key=lambda o: o["label"])
    minor_options.sort(key=lambda o: o["label"])
    return render_template(
        "home.html",
        options=options,
        plan_text=plan_text,
        selected_majors=selected_majors,
        selected_minors=selected_minors,
        prior_text=prior_text,
        minor_options=minor_options,
    )


def build_rows(report):
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

    return rows


@app.route("/audit", methods=["POST"])
def audit_page():
    text = request.form["plan"]
    plan = []

    prior_raw = request.form.get("prior", "")
    prior_raw = prior_raw.replace("\n", ",")

    prior = {piece.strip().upper() for piece in prior_raw.split(",") if piece.strip()}

    chosen_majors = []
    major_seen = set()

    for choice in request.form.getlist("major"):
        if not choice or choice in major_seen:
            continue
        else:
            chosen_majors.append(choice)
            major_seen.add(choice)

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        semester = [piece.strip().upper() for piece in line.split(",") if piece.strip()]
        plan.append(semester)

    all_courses = set(prior)

    for semester in plan:
        all_courses.update(semester)

    chosen_minors = []
    minor_seen = set()

    for choice in request.form.getlist("minor"):
        if not choice or choice in minor_seen:
            continue
        else:
            chosen_minors.append(choice)
            minor_seen.add(choice)

    minor_results = []

    for poid in chosen_minors:
        result = is_satisfied(minors[poid]["rule"], all_courses, set())

        if result is True:
            status = "complete"
        elif result is False:
            status = "not complete"
        else:
            status = "needs advisor check"

        minor_results.append({"title": minors[poid]["title"], "status": status})

    programs = []

    for choice in chosen_majors:
        poid, index = choice.split("|")
        track = degrees[poid]["tracks"][int(index)]
        program = degrees[poid]

        if track["name"] in program["title"]:
            title = program["title"]
        else:
            title = f"{program['title']} - {track['name']}"

        report = audit(plan, prior, track, GENED_SETS)
        rows = build_rows(report)
        total = check_total_hours(plan, prior, track)
        programs.append({"title": title, "rows": rows, "total": total})

    prereq_problems = check_plan(plan, prior, courses)
    hours = check_hours(plan, courses, max_hours=19, approved_max=21, min_hours=12)

    return render_template(
        "audit.html",
        prereq_problems=prereq_problems,
        hours=hours,
        programs=programs,
        minor_results=minor_results,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
