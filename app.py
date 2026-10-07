from flask import Flask, render_template, request
from planner.rules import (
    audit,
    GENED_SETS,
    check_total_hours,
    check_plan,
    courses,
    check_hours,
    is_satisfied,
    minor_rows,
    build_requirements,
    used_courses,
    slot_kind,
    parse_credits,
    describe,
    slot_base,
    LAB_COURSES,
)
from planner.recommend import (
    recommended_plan,
    merge_plans,
    minor_courses,
    place_course,
    semester_codes,
    entry_hours,
)

import json

with open("data/degrees.json", "r", encoding="utf-8") as f:
    degrees = json.load(f)

with open("data/minorsfinal.json", "r", encoding="utf-8") as f:
    minors = json.load(f)

elective_map = {}

for code in courses:
    prefix, number = code.split()
    number = int(number)

    if number >= 5000:
        continue
    else:
        elective_map.setdefault(prefix, []).append(code)

ELECTIVE_GROUPS = []

for prefix in sorted(elective_map):
    ELECTIVE_GROUPS.append({"subject": prefix, "codes": sorted(elective_map[prefix])})

COURSE_INFO = {}

for code, info in courses.items():
    text = f"{info.get('title')} ({info.get('credits')})\nPrereqs: {describe(info.get('prereq_rule'))}"

    if info.get("description"):
        text += "\n" + info.get("description")[:200]

    COURSE_INFO[code] = text


app = Flask(__name__)


def clean_choices(values):
    chosen = []
    seen = set()

    for choice in values:
        if not choice or choice in seen:
            continue
        else:
            chosen.append(choice)
            seen.add(choice)

    return chosen


def parse_prior(text):
    text = text.replace("\n", ",")
    prior = {piece.strip().upper() for piece in text.split(",") if piece.strip()}
    return prior


@app.route("/", methods=["GET", "POST"])
def home():
    options = []
    minor_options = []
    plan_text = ""
    plan = []
    plan_view = []
    palette = []
    planned = set()
    total_hours = 0

    selected_majors = ["", "", ""]
    selected_minors = ["", "", ""]
    prior_text = ""

    if request.method == "POST":
        selected_majors = request.form.getlist("major")
        selected_minors = request.form.getlist("minor")
        prior_text = request.form.get("prior", "")

        plans = []

        for choice in clean_choices(selected_majors):
            poid, index = choice.split("|")
            track = degrees[poid]["tracks"][int(index)]
            plans.append(recommended_plan(track))

            program = degrees[poid]

            if track["name"] in program["title"]:
                title = program["title"]
            else:
                title = f"{program['title']} - {track['name']}"

            reqs = build_requirements(track)
            codes = []
            slot_groups = {}

            for req in reqs:
                if req["type"] != "course":
                    desc = req["slot"]["description"]

                    kind_info = slot_kind(req["slot"], track)

                    if kind_info["kind"] == "list":
                        slot_codes = kind_info["courses"]
                    elif kind_info["kind"] == "subject":
                        slot_codes = []

                        for code in courses:
                            prefix, number = code.split()
                            number = int(number)

                            if number >= 5000:
                                continue

                            if prefix in kind_info["subjects"] and (
                                kind_info["min_level"] is None
                                or number >= kind_info["min_level"]
                            ):
                                slot_codes.append(code)
                    else:
                        continue

                    credits = parse_credits(req["slot"]["credits"])

                    if credits is None:
                        hours = 3
                    else:
                        hours = credits[0]

                    base = slot_base(desc, req["slot"]["credits"])
                    key = tuple(sorted(slot_codes))

                    if key in slot_groups:
                        slot_groups[key]["hours"] += hours
                    else:
                        slot_groups[key] = {
                            "title": base,
                            "hours": hours,
                            "codes": sorted(slot_codes),
                        }

                else:
                    codes.extend(req["options"])

            palette.append({"title": title, "codes": codes, "key": title})

            for group in slot_groups.values():
                palette.append(
                    {
                        "title": f"{group['title']}",
                        "codes": group["codes"],
                        "key": group["title"]
                    }
                )

        plan = merge_plans(plans)

        prior = parse_prior(prior_text)
        planned = set(prior)

        for semester in plan:
            planned.update(semester_codes(semester))

        for poid in clean_choices(selected_minors):
            picks = minor_courses(minors[poid]["rule"], planned)
            mentioned = used_courses(minors[poid]["rule"], set(courses))

            palette.append(
                {"title": minors[poid]["title"], "codes": sorted(set(mentioned)), "key": minors[poid]["title"]}
            )

            for code in picks:
                place_course(plan, code, prior)
                planned.add(code)

        gened_sections = []

        for category, codes in GENED_SETS.items():
            gened_sections.append({"title": category, "codes": sorted(codes), "key": category})
        
        gened_sections.append({"title": "Natural Sciences Lab", "key": "Natural Sciences Lab", "codes": LAB_COURSES})

        gened_sections.sort(key=lambda s:s["title"])
        palette.extend(gened_sections)

        lines = []

        for semester in plan:
            hours = 0

            for e in semester:
                hours += entry_hours(e)

            plan_view.append({"entries": semester, "hours": hours})
            total_hours += hours

            codes = [e["code"] for e in semester if e["type"] == "course"]
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
        plan_view=plan_view,
        total_hours=total_hours,
        palette=palette,
        planned=planned,
        elective_groups=ELECTIVE_GROUPS,
        course_info=COURSE_INFO,
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

    prior = parse_prior(request.form.get("prior", ""))

    chosen_majors = clean_choices(request.form.getlist("major"))

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        semester = [piece.strip().upper() for piece in line.split(",") if piece.strip()]
        plan.append(semester)

    all_courses = set(prior)

    for semester in plan:
        all_courses.update(semester)

    chosen_minors = clean_choices(request.form.getlist("minor"))

    minor_results = []

    for poid in chosen_minors:
        result = is_satisfied(minors[poid]["rule"], all_courses, set())

        if result is True:
            status = "complete"
        elif result is False:
            status = "not complete"
        else:
            status = "needs advisor check"

        minor_results.append(
            {
                "title": minors[poid]["title"],
                "status": status,
                "rows": minor_rows(minors[poid]["rule"], all_courses),
            }
        )

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
