import app, random, math
from planner.rules import check_plan, courses, parse_credits
from planner.recommend import END_SEQUENCE
from collections import Counter


def fake_render(template, **context):
    return context


app.render_template = fake_render

majors = []
minors = []
RUNS = 1000

for poid, program in app.degrees.items():
    for i, track in enumerate(program["tracks"]):
        majors.append(f"{poid}|{i}")

for key in app.minors:
    minors.append(key)

for mode in ["fast", "balanced"]:
    # default should b 42
    # also tested 2026
    random.seed(42)

    flagged_courses = Counter()
    flagged_majors = Counter()

    crashes = 0
    long_plans = 0
    over_19 = 0
    dupes = 0
    prereq = 0
    unknown = 0
    crash_ex = []
    minor_drops = 0
    drop_ex = []
    end_shared = 0
    under_total = 0
    under_ex = []

    for n in range(RUNS):
        major_num = random.choice([1, 1, 1, 2, 2, 3])
        dif_majors = random.sample(majors, major_num)

        minor_num = random.choice([0, 0, 1, 1, 1, 2, 2, 3])
        dif_minors = random.sample(minors, minor_num)

        dif_majors += [""] * (3 - len(dif_majors))
        dif_minors += [""] * (3 - len(dif_minors))

        form_data = {
            "major": dif_majors,
            "minor": dif_minors,
            "prior": "",
            "mode": mode,
        }

        try:
            with app.app.test_request_context("/", method="POST", data=form_data):
                result = app.home()
        except Exception as e:
            crashes += 1
            crash_ex.append((dif_majors, dif_minors, repr(e)))
            continue

        plan_view = result["plan_view"]
        where = {}

        for i, semester in enumerate(plan_view):
            for e in semester["entries"]:
                if e["type"] == "course" and e["code"] in END_SEQUENCE:
                    where[e["code"]] = i

        if len(set(where.values())) < len(where):
            end_shared += 1

        need = 0

        for major in dif_majors:
            if major == "":
                continue

            poid, index = major.split("|")
            track = app.degrees[poid]["tracks"][int(index)]
            t = parse_credits(track.get("total_hours"))

            if t:
                need = max(need, t[0])

        have = sum(sem["hours"] for sem in plan_view)

        if have < need:
            under_total += 1
            under_ex.append((dif_majors, dif_minors, have, need))

        if len(plan_view) > 8:
            long_plans += 1

        for sem in plan_view:
            if sem["hours"] > 19:
                over_19 += 1

        plan_codes = []
        slot_hours = []

        for sem in plan_view:
            codes = []
            slot_total = 0

            for e in sem["entries"]:
                if e["type"] == "course":
                    codes.append(e["code"])
                elif e["type"] == "slot":
                    slot_total += e["hours"]

            plan_codes.append(codes)
            slot_hours.append(slot_total)

            if len(codes) != len(set(codes)):
                dupes += 1

        problems = check_plan(plan_codes, set(), courses, extra=slot_hours)

        for sem_num, code, reason in problems:
            if reason == "prereqs not met":
                prereq += 1
                flagged_courses[code] += 1

                for major in dif_majors:
                    if major == "":
                        continue
                    flagged_majors[major] += 1
            elif reason == "unknown course":
                unknown += 1

        if minor_num > 0 and major_num == 1:
            no_minor_data = {
                "major": dif_majors,
                "minor": ["", "", ""],
                "prior": "",
                "mode": mode,
            }

            with app.app.test_request_context("/", method="POST", data=no_minor_data):
                no_minor_result = app.home()

            with_hours = sum(sem["hours"] for sem in plan_view)
            without_hours = sum(sem["hours"] for sem in no_minor_result["plan_view"])

            if with_hours < without_hours:
                minor_drops += 1
                drop_ex.append((dif_majors, dif_minors, with_hours, without_hours))

    print(mode)

    print("crashes:", crashes)
    print("long plans:", long_plans)
    print("over 19 hours:", over_19)
    print("prereqs not found:", prereq)
    print("unknown course:", unknown)
    print("duplicates:", dupes)
    print("minor lowered hours:", minor_drops)
    print("end sequence shared:", end_shared)
    print("under degree total:", under_total)

    for ex in crash_ex[:5]:
        print(ex)

    for ex in drop_ex[:5]:
        print(ex)

    for ex in under_ex[:5]:
        print(ex)

    for code, count in flagged_courses.most_common(10):
        print(code, count)

    for major, count in flagged_majors.most_common(5):
        poid, index = major.split("|")
        title = app.degrees[poid]["tracks"][int(index)]["name"]
        print(major, count, title)
