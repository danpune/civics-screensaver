#!/usr/bin/env python3
"""Build web/index.html and web/img/ from the site's data and pictures.json.

  python3 make_slides.py            uses ../greencard-checklist for the questions
  SITE=/path/to/site python3 make_slides.py

Needs Pillow, to make the pictures smaller. The page it writes holds everything and needs no network.
"""
import json, os, re, shutil
from datetime import date
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get("SITE", os.path.join(HERE, "..", "greencard-checklist"))
WIDE = 1440   # longest side of a picture, in pixels

def load(name):
    return json.load(open(os.path.join(SITE, name), encoding="utf-8"))

questions, why, officials = load("questions.json"), load("why.json")["why"], load("officials.json")
federal = officials["parts"]["federal"]   # the names that change: questions 30, 38, 39 and 57
day = date.fromisoformat(officials["changed"])
CHECKED = "Names from uscis.gov/citizenship/testupdates, checked %s %d, %d." % (day.strftime("%b"), day.day, day.year)
FIND = " Find your own answer at danpune.github.io/greencard-checklist/civics.html"   # the four answers that depend on where you live
pictures = json.load(open(os.path.join(HERE, "pictures.json"), encoding="utf-8"))

def need(q):   # how many answers the question asks for, as on the site
    m = re.search(r"\b(?:name|what are) (two|three|five)\b", q, re.I)
    return {"two": 2, "three": 3, "five": 5}[m.group(1).lower()] if m else 1

out = os.path.join(HERE, "web")
shutil.rmtree(out, ignore_errors=True)
os.makedirs(os.path.join(out, "img"))

slides = []
for q in questions:
    i, n = str(q["id"]), need(q["q"])
    answers = federal[i] if i in federal else q["a"]   # every form of the name that USCIS accepts
    pa = pictures.get(i, {}).get("answer")   # the accepted answer the picture shows is listed first
    if pa:
        assert pa in answers, (i, pa)
        answers = [pa] + [a for a in answers if a != pa]
    shown = answers[:max(n, 4)]
    s = {"id": q["id"], "sec": q["sec"], "star": bool(q.get("star")), "q": q["q"], "need": n,
         "a": shown, "more": len(answers) - len(shown), "note": CHECKED if i in federal else (q.get("note", "") + FIND if q["id"] in (23, 29, 61, 62) else q.get("note", "")), "why": why[i]["w"]}
    p = pictures.get(i)
    if p:
        im = Image.open(os.path.join(HERE, "pictures", p["file"])).convert("RGBA")
        bg = Image.new("RGB", im.size, (11, 29, 54)); bg.paste(im, mask=im.getchannel("A")); im = bg   # transparent edges take the page colour
        im.thumbnail((WIDE, WIDE), Image.LANCZOS)
        im.save(os.path.join(out, "img", i + ".jpg"), quality=80, optimize=True, progressive=True)
        s["img"] = {"src": "img/%s.jpg" % i, "caption": p["caption"], "credit": p["credit"]}
    slides.append(s)

assert len(slides) == 128 and [s["id"] for s in slides] == list(range(1, 129))
assert all(s["q"] and s["a"] and s["why"] for s in slides)
assert all(len(s["a"]) >= s["need"] for s in slides)

page = open(os.path.join(HERE, "slides.html"), encoding="utf-8").read()
assert page.count("/*DATA*/") == 1
data = json.dumps(slides, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page.replace("/*DATA*/", data))
size = sum(os.path.getsize(os.path.join(out, "img", f)) for f in os.listdir(os.path.join(out, "img")))
print("web/index.html: 128 questions, %d with a picture, pictures %.1f MB" % (sum("img" in s for s in slides), size / 1e6))
