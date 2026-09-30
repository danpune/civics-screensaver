#!/usr/bin/env python3
"""Make the study videos from the same slides as the screensaver, with a title, a description and chapters for each.

  python3 make_videos.py            all five videos into videos/
  python3 make_videos.py full       only one: full, star, test1, test2 or test3

Run make_slides.py first (build.sh does). Needs Python 3 and the Xcode Command Line Tools; nothing is downloaded.
"""
import json, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "videos")   # not build/: build.sh empties that folder
PAGE = os.path.join(HERE, "web", "index.html")
SITE = "danpune.github.io/greencard-checklist/civics.html"
REPO = "github.com/danpune/civics-screensaver"

html = open(PAGE, encoding="utf-8").read()
D = json.loads(re.search(r"var D = (\[.*?\]);   //", html, re.S).group(1))
Q = {s["id"]: s for s in D}
STATE, NAMES = (23, 29, 61, 62), (30, 38, 39, 57)
checked = re.search(r"checked ([A-Z][a-z]{2} \d+, \d{4})", Q[38]["note"]).group(1)
SECTIONS = []
for s in D:
    if s["sec"] not in SECTIONS:
        SECTIONS.append(s["sec"])

QUESTION = 5.0   # seconds, as in the screensaver
def answer_time(s):   # the screensaver's rule: longer answers stay longer
    words = len((" ".join(s["a"]) + " " + s.get("why", "") + " " + s.get("note", "")).split())
    return max(8.0, min(30.0, 5 + words * 0.26))

UNOFFICIAL = "Unofficial study aid. Not made by USCIS or any government agency. Not legal advice."
def intro(k, h, lines):
    return {"card": {"k": k, "h": h, "lines": lines}, "sec": 12.0}   # YouTube shows no chapter shorter than 10 seconds
SOURCES = {"card": {"k": "Sources", "h": "Check the official pages before your interview", "lines": [
    "Questions and answers: USCIS M-1778 (09/25), on uscis.gov.",
    "The names of office holders change: check uscis.gov/citizenship/testupdates.",
    "Practice with your own state's answers: " + SITE,
    "Pictures: public domain in the U.S. or CC0. Credits: " + REPO]}, "sec": 10.0}

def qa(ids):
    out = []
    for i in ids:
        out += [{"q": i, "side": "q", "sec": QUESTION}, {"q": i, "side": "a", "sec": round(answer_time(Q[i]), 2)}]
    return out

def plans():
    p = {}
    full = [intro("Unofficial study aid", "All 128 questions of the 2025 U.S. citizenship civics test", [
        "Each question is shown first. The answer, a picture and a short explanation follow after 5 seconds. Pause the video to take more time.",
        "The names of the President, Vice President, Speaker and Chief Justice are as checked on " + checked + ". Check them again before your interview.",
        UNOFFICIAL])]
    for n, sec in enumerate(SECTIONS, 1):
        full.append({"card": {"k": "Part %d of %d" % (n, len(SECTIONS)), "h": sec, "lines": []}, "sec": 3.0, "chapter": sec})
        full += qa([s["id"] for s in D if s["sec"] == sec])
    p["full"] = full + [SOURCES]

    star = [s["id"] for s in D if s["star"]]
    p["star"] = [intro("Unofficial study aid", "The 20 questions for the 65/20 exception", [
        "If you are 65 or older and have lived in the United States as a permanent resident for 20 years or more, you may study just these 20 questions. The officer asks 10 of them; you need at least 6 right. You may also take the test in the language of your choice.",
        "Each question is shown first, then the answer. Pause the video to take more time.",
        UNOFFICIAL])] + qa(star) + [SOURCES]

    # three practice tests of 20, with no question twice; leave out the answers that depend on where you live or on who holds office
    pool = [s["id"] for s in D if s["id"] not in STATE + NAMES]
    random.Random(2025).shuffle(pool)
    for t in range(3):
        ids = pool[t * 20:(t + 1) * 20]
        p["test%d" % (t + 1)] = [intro("Unofficial practice test %d of 3" % (t + 1), "20 questions, like the civics test", [
            "Say your answer out loud before the answer appears. Pause the video if you need more time.",
            "Count your right answers. In the real test the officer stops when you reach 12 right answers (you pass) or 9 wrong ones.",
            UNOFFICIAL])] + qa(ids) + [{"card": {"k": "End of practice test %d" % (t + 1), "h": "How many did you get right?", "lines": [
                "12 right answers pass the 2025 civics test. Practice the ones you missed at " + SITE, "Sources: uscis.gov and " + REPO]}, "sec": 10.0}]
    return p

TITLES = {
    "full": "2025 U.S. Citizenship Test: all 128 civics questions and answers, with pictures (unofficial)",
    "star": "2025 U.S. Citizenship Test: the 20 questions for 65/20 applicants, with answers (unofficial)",
    "test1": "2025 U.S. Citizenship Test: civics practice test 1 of 3, 20 questions (unofficial)",
    "test2": "2025 U.S. Citizenship Test: civics practice test 2 of 3, 20 questions (unofficial)",
    "test3": "2025 U.S. Citizenship Test: civics practice test 3 of 3, 20 questions (unofficial)",
}

def stamp(t):
    t = int(t)
    return "%d:%02d:%02d" % (t // 3600, t % 3600 // 60, t % 60) if t >= 3600 else "%d:%02d" % (t // 60, t % 60)

def description(key, plan):
    marks, t, qn = [("0:00", "Introduction")], 0.0, 0
    for s in plan:
        if key == "full" and s.get("chapter"):
            marks.append((stamp(t), s["chapter"]))
        if key != "full" and s.get("side") == "q":
            qn += 1
            q = Q[s["q"]]["q"]   # numbered 1 to 20 in this video; the slide shows the official number
            marks.append((stamp(t), "%d. %s" % (qn, q if len(q) <= 70 else q[:69].rsplit(" ", 1)[0] + "…")))
        if s.get("card", {}).get("k") == "Sources" or s.get("card", {}).get("k", "").startswith("End of"):
            marks.append((stamp(t), "Sources" if key == "full" or key == "star" else "Your score"))
        t += s["sec"]
    at = [sum(int(x) * 60 ** n for n, x in enumerate(reversed(m[0].split(":")))) for m in marks]
    assert all(b - a >= 10 for a, b in zip(at, at[1:] + [int(t)])), key + ": YouTube shows no chapter shorter than 10 seconds"
    lines = [TITLES[key], "",
             UNOFFICIAL,
             "This is the 2025 test, for people who file Form N-400 on or after October 20, 2025. If you filed earlier, you take the 2008 test.",
             "Each question is shown for 5 seconds, then the answer, a picture and a short explanation. Pause the video to take more time.", ""]
    if key in ("full", "star"):
        lines += ["The names of the President, Vice President, Speaker of the House and Chief Justice are as checked on %s. They change; "
                  "check them at https://www.uscis.gov/citizenship/testupdates before your interview. Questions that depend on where you "
                  "live (senators, representative, governor, capital): find your own answers at https://%s" % (checked, SITE), ""]
    if key.startswith("test"):
        lines += ["The 20 questions were picked at random from the 128, leaving out the 8 whose answers depend on where you live or on "
                  "who holds office. In the real test the officer asks up to 20 questions and stops when you reach 12 right answers "
                  "(you pass) or 9 wrong ones.", ""]
    lines += ["Chapters:"] + ["%s %s" % m for m in marks] + ["",
              "Practice with your own state's answers, a mock test and interview practice: https://" + SITE,
              "Free Mac screensaver with the same slides: https://" + REPO, "",
              "Sources:",
              "128 Civics Questions and Answers (2025 version), USCIS M-1778 (09/25): https://www.uscis.gov/sites/default/files/document/questions-and-answers/2025-Civics-Test-128-Questions-and-Answers.pdf",
              "2025 Civics Test, USCIS: https://www.uscis.gov/citizenship-resource-center/naturalization-test-and-study-resources/2025-civics-test",
              "Check for Test Updates, USCIS: https://www.uscis.gov/citizenship/testupdates",
              "Explanations: written for the practice site, based on One Nation, One People: The USCIS 2025 Civics Test Study Guide: https://www.uscis.gov/sites/default/files/document/brochures/USCIS-2025-Civics-Test-Study-Guide.pdf",
              "Pictures: public domain in the United States or CC0, from Wikimedia Commons. Credit and source of each: https://%s/blob/main/CREDITS.md" % REPO,
              "Background sound: made for this video from simple tones and soft noise; no one owns it.", ""]
    return "\n".join(lines), len(marks), t

assert all(len(t) <= 100 for t in TITLES.values()), "YouTube titles are limited to 100 characters"

def main():
    want = sys.argv[1:] or ["full", "star", "test1", "test2", "test3"]
    os.makedirs(OUT, exist_ok=True)
    tool = os.path.join(OUT, "video")
    subprocess.run(["swiftc", "-O", "-swift-version", "5", os.path.join(HERE, "Tools", "video.swift"), "-o", tool], check=True, capture_output=True)
    for key, plan in plans().items():
        if key not in want:
            continue
        text, chapters, seconds = description(key, plan)
        open(os.path.join(OUT, key + ".txt"), "w", encoding="utf-8").write(text)
        json.dump({"slides": [{k: v for k, v in s.items() if k != "chapter"} for s in plan], "sound": True},
                  open(os.path.join(OUT, key + ".plan.json"), "w"))
        print("%s: %d slides, %d chapters, %s" % (key, len(plan), chapters, stamp(seconds)))
        subprocess.run([tool, PAGE, os.path.join(OUT, key + ".plan.json"), os.path.join(OUT, key + ".mp4"), os.path.join(OUT, key + "-thumbnail.jpg")], check=True)

if __name__ == "__main__":
    main()
