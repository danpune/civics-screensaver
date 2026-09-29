#!/usr/bin/env python3
"""Download the chosen pictures and write pictures.json and CREDITS.md.

  python3 get_pictures.py picks.json

picks.json is a list of pictures, one per question: id, found, file_title, page_url, image_url, license, basis,
credit, caption. Every picture is public domain or CC0; the licence of each was checked twice before it got here.
Stdlib only. A picture that is already in pictures/ is not downloaded again.
"""
import json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "civics-study-aid/1.0 (https://danpune.github.io/greencard-checklist/)"}
OK = ("public domain", "pd", "cc0")   # how a free licence is spelled on Wikimedia Commons

picks = [p for p in json.load(open(sys.argv[1], encoding="utf-8")) if p.get("found")]
os.makedirs(os.path.join(HERE, "pictures"), exist_ok=True)
manifest, credits = {}, []
for p in sorted(picks, key=lambda p: p["id"]):
    assert any(w in p["license"].lower() for w in OK), "question %s: licence %r is not free" % (p["id"], p["license"])
    assert p["image_url"].startswith(("https://upload.wikimedia.org/", "https://thumb.wikimedia.org/")), p["image_url"]
    ext = ".png" if p["image_url"].lower().split("?")[0].endswith(".png") else ".jpg"
    name = "%03d%s" % (p["id"], ext)
    path = os.path.join(HERE, "pictures", name)
    if not os.path.exists(path) or p.get("crop"):
        with urllib.request.urlopen(urllib.request.Request(p["image_url"].split("?")[0], headers=UA), timeout=90) as r:
            data = r.read()
        assert len(data) > 20000, "question %s: the download is too small to be a picture" % p["id"]
        open(path, "wb").write(data)
        if p.get("crop"):   # left, top, right, bottom in pixels of the downloaded copy: cuts off the edge of a glass negative
            from PIL import Image
            Image.open(path).convert("RGB").crop(p["crop"]).save(path, quality=92)
        time.sleep(1)   # be gentle with Wikimedia's servers
    manifest[str(p["id"])] = {"file": name, "caption": p["caption"], "credit": p["credit"],
                              "source": p["page_url"], "license": p["license"], "basis": p["basis"]}
    credits.append("| %d | %s | %s | %s | [file page](%s) |" % (p["id"], p["caption"], p["credit"], p["license"], p["page_url"]))

json.dump(manifest, open(os.path.join(HERE, "pictures.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
open(os.path.join(HERE, "CREDITS.md"), "w", encoding="utf-8").write(
    "# Picture credits\n\nEvery picture is in the public domain or released as CC0. Each was found on Wikimedia Commons and its "
    "licence was checked by two separate reviewers.\n\n| Question | Picture | Credit | Licence | Source |\n|---|---|---|---|---|\n"
    + "\n".join(credits) + "\n")
print("%d pictures, pictures.json and CREDITS.md written" % len(manifest))
