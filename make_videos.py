#!/usr/bin/env python3
"""Make the study videos from the same slides as the screensaver, and everything needed to upload them to YouTube.

  python3 make_videos.py            all five videos into videos/, with their descriptions and videos/upload.html
  python3 make_videos.py full       only one: full, star, test1, test2 or test3
  python3 make_videos.py text       only the descriptions and upload.html, without making the videos

Run make_slides.py first (build.sh does). Needs Python 3 and the Xcode Command Line Tools; nothing is downloaded.
"""
import html as H, json, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "videos")   # not build/: build.sh empties that folder
PAGE = os.path.join(HERE, "web", "index.html")
SITE = "danpune.github.io/greencard-checklist/civics.html"
REPO = "github.com/danpune/civics-screensaver"
IN_USE = 2026   # the 2025 test was still in use when this was checked on uscis.gov (2026-09-29); check again before changing it

page = open(PAGE, encoding="utf-8").read()
D = json.loads(re.search(r"var D = (\[.*?\]);   //", page, re.S).group(1))
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
    p["star"] = [intro("Unofficial study aid", "The 20 questions for 65/20 special consideration", [
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

# YouTube metadata. The words people search for come first, because phones cut titles after about 50 characters.
USED = "(used in %d, Unofficial)" % IN_USE
TITLES = {
    "full": "US Citizenship Test 2025: 128 Civics Questions & Answers with Pictures " + USED,
    "star": "65/20 US Citizenship Test 2025: the 20 Civics Questions & Answers " + USED,
    "test1": "US Citizenship Test 2025: Civics Practice Test 1 of 3, 20 Questions " + USED,
    "test2": "US Citizenship Test 2025: Civics Practice Test 2 of 3, 20 Questions " + USED,
    "test3": "US Citizenship Test 2025: Civics Practice Test 3 of 3, 20 Questions " + USED,
}
# YouTube: tags "play a minimal role", mostly for misspellings (support.google.com/youtube/answer/146402). Only true ones.
BASE = ["us citizenship test", "citizenship test %d" % IN_USE, "us citizenship test 2025", "2025 civics test", "2025 naturalization civics test",
        "civics test", "civic test", "naturalization test", "naturalisation test", "uscis civics test", "n-400", "n400", "citizenship interview"]
TEST = ["citizenship practice test", "civics practice test", "20 random civics questions", "citizenship test quiz", "mock civics test"]
TAGS = {
    "full": BASE + ["128 civics questions", "128 civics questions and answers", "civics questions with pictures", "civics test in order"],
    "star": BASE + ["65/20", "65 20", "65/20 exemption", "65/20 special consideration", "65/20 civics questions", "20 civics questions", "65/20 rule"],
    "test1": BASE + TEST, "test2": BASE + TEST, "test3": BASE + TEST,
}
HASHTAGS = {"full": "#CitizenshipTest #CivicsTest #NaturalizationTest", "star": "#CitizenshipTest #CivicsTest #NaturalizationTest",
            "test1": "#CitizenshipTest #CivicsTest #PracticeTest", "test2": "#CitizenshipTest #CivicsTest #PracticeTest",
            "test3": "#CitizenshipTest #CivicsTest #PracticeTest"}
PLAYLIST = ("US Citizenship Test 2025: 128 Civics Questions, 65/20 and Practice Tests (Unofficial)",
            "Unofficial study videos for the 2025 U.S. naturalization civics test, still in use in %d: all 128 questions with pictures and "
            "short explanations, the 20 questions for 65/20 applicants, and three 20-question practice tests. Not made by or affiliated "
            "with USCIS or any government agency. Not legal advice." % IN_USE)
CHANNEL = ("Unofficial study aids for the U.S. naturalization civics test. Not made by or affiliated with USCIS or any government agency. "
           "Not legal advice.")

def tag_length(tags):   # as YouTube counts: a tag with a space gets quotes, and the commas count (developers.google.com/youtube/v3/docs/videos)
    return sum(len(t) + (2 if " " in t else 0) for t in tags) + len(tags) - 1

for k in TITLES:
    assert len(TITLES[k]) <= 100 and not re.search("[<>]", TITLES[k]), k + ": YouTube titles are limited to 100 characters, without < or >"
    assert tag_length(TAGS[k]) <= 500 and len(set(TAGS[k])) == len(TAGS[k]), k + ": YouTube allows 500 characters of tags"

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
        t += s["sec"]
    at = [sum(int(x) * 60 ** n for n, x in enumerate(reversed(m[0].split(":")))) for m in marks]
    assert all(b - a >= 10 for a, b in zip(at, at[1:] + [int(t)])), key + ": YouTube shows no chapter shorter than 10 seconds"

    in_use = ("The 2025 civics test is still in use in %d for anyone who filed Form N-400 on or after October 20, 2025. "
              "If you filed earlier, you take the 2008 test (100 questions)." % IN_USE)
    unofficial = "Unofficial study aid. Not made by or affiliated with USCIS or any government agency. Not legal advice."
    def names(who, where):
        return ("The names of the %s are as checked on %s. They change; check them at https://www.uscis.gov/citizenship/testupdates "
                "before your interview. %s: find your own answers at https://%s" % (who, checked, where, SITE))
    shown = "Each question is shown for 5 seconds, then the answer, a picture and a short explanation. Pause the video to take more time."
    if key == "full":   # the first lines are what YouTube shows before "more", so each video starts differently
        lines = ["All 128 questions and answers of the 2025 U.S. naturalization civics test, in the official order, with pictures "
                 "and short explanations.", in_use, unofficial, "", shown, "",
                 names("President, Vice President, Speaker of the House and Chief Justice", "Questions that depend on where you live (senators, representative, governor, capital)")]
    elif key == "star":
        lines = ["The 20 questions for 65/20 special consideration on the 2025 U.S. naturalization civics test, with answers, pictures "
                 "and short explanations.",
                 "65/20 is for people who are 65 or older and have lived in the United States as a permanent resident for 20 years or "
                 "more when they file Form N-400. The officer asks 10 of these 20 questions; 6 right answers pass. You may take the civics "
                 "test in the language of your choice, with an interpreter you bring to the interview. Everyone else studies all 128 questions.",
                 in_use, unofficial, "", shown, "", names("President, Vice President and Speaker of the House", "The question about your governor depends on where you live"), "",
                 "These are the 20 questions marked with an asterisk (*) in the official list, USCIS M-1778 (09/25). USCIS's Check for Test "
                 "Updates page marks a few questions differently: it marks question 23 (one of your state's U.S. senators) and does not "
                 "mark questions 30, 39 and 61. This video follows the M-1778 list. To be safe, learn question 23 too."]
    else:
        lines = ["Practice test %s of 3 for the 2025 U.S. naturalization civics test: 20 questions picked at random from the official 128 "
                 "(leaving out the 8 explained below), like the real test. Say each answer out loud before it appears and count your right answers: 12 right answers pass."
                 % key[-1], in_use, unofficial, "", shown, "",
                 "The questions leave out the 8 whose answers depend on where you live or on who holds office. The three practice tests "
                 "have no question in common. In the real test the officer asks up to 20 questions and stops when you reach 12 right "
                 "answers (you pass) or 9 wrong ones."]
    lines += ["", "Chapters:"] + ["%s %s" % m for m in marks] + ["",
              "Practice with your own state's answers, a mock test and interview practice: https://" + SITE,
              "Free Mac screensaver with the same slides: https://" + REPO, "",
              "Sources:",
              "128 Civics Questions and Answers (2025 version), USCIS M-1778 (09/25): https://www.uscis.gov/sites/default/files/document/questions-and-answers/2025-Civics-Test-128-Questions-and-Answers.pdf",
              "2025 Civics Test, USCIS: https://www.uscis.gov/citizenship-resource-center/naturalization-test-and-study-resources/2025-civics-test",
              "Check for Test Updates, USCIS: https://www.uscis.gov/citizenship/testupdates",
              "Explanations: written for the practice site, mainly based on One Nation, One People: The USCIS 2025 Civics Test Study Guide (standard history references where the guide says nothing): https://www.uscis.gov/sites/default/files/document/brochures/USCIS-2025-Civics-Test-Study-Guide.pdf",
              "Pictures: public domain in the United States or CC0, from Wikimedia Commons. Credit and source of each: https://%s/blob/main/CREDITS.md" % REPO,
              "Background sound: made for this video from simple tones and soft noise; no one owns it.", "",
              HASHTAGS[key]]
    text = "\n".join(lines)
    assert len(text.encode("utf-8")) <= 5000 and not re.search("[<>]", text), key + ": YouTube descriptions are limited to 5,000 bytes"
    return text, len(marks), t

NAMES_OF = {"full": "All 128 questions", "star": "The 20 questions for 65/20", "test1": "Practice test 1", "test2": "Practice test 2", "test3": "Practice test 3"}

def upload_page(texts):
    """videos/upload.html: every step and every field, with copy buttons, for uploading the videos by hand in YouTube Studio."""
    n = [0]
    def field(label, value, rows=0):
        n[0] += 1
        box = ('<textarea id="f%d" rows="%d" readonly>%s</textarea>' % (n[0], rows, H.escape(value)) if rows
               else '<input id="f%d" value="%s" readonly>' % (n[0], H.escape(value)))
        return '<div class="f"><div class="l"><span>%s</span> <button onclick="cp(%d, this)">Copy</button></div>%s</div>' % (label, n[0], box)
    cards = []
    for key, text in texts.items():
        cards.append('<section><h2>%s</h2><p class="file">Video file: <b>%s.mp4</b> &middot; Thumbnail: <b>%s-thumbnail.jpg</b></p>'
                     '<img src="%s-thumbnail.jpg" alt="">%s%s%s</section>' % (
                         NAMES_OF[key], key, key, key, field("Title", TITLES[key]), field("Description", text, 12),
                         field("Tags (under Show more)", ", ".join(TAGS[key]))))
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>YouTube upload sheet</title><style>
:root{--bg:#f6f4ee;--card:#fff;--ink:#1b2432;--muted:#5b6474;--line:#d9d5ca;--accent:#1f4f8f}
@media (prefers-color-scheme:dark){:root{--bg:#0e1522;--card:#172133;--ink:#eef1f6;--muted:#a3adbd;--line:#2c3a52;--accent:#8db4ee}}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:26px;margin:0 0 4px}h2{font-size:20px;margin:0 0 8px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:18px 0}
ol,ul{padding-left:22px}li{margin:6px 0}.muted,.file{color:var(--muted)}
img{width:100%%;max-width:420px;border-radius:8px;display:block;margin:8px 0 12px}
.f{margin:10px 0}.l{font-weight:600;display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}
input,textarea{width:100%%;box-sizing:border-box;font:14px/1.4 ui-monospace,Menlo,monospace;padding:8px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink)}
button{font:600 14px system-ui;padding:6px 14px;border-radius:8px;border:1px solid var(--accent);background:var(--accent);color:var(--card);cursor:pointer}
a{color:var(--accent)}
</style></head><body><main>
<h1>YouTube upload sheet</h1>
<p class="muted">Five unofficial study videos for the 2025 U.S. civics test. Everything to type in YouTube Studio is below, with a Copy button.
The files are in the same folder as this page.</p>

<section><h2>1. Once, before the first upload</h2><ol>
<li>Open <a href="https://studio.youtube.com">studio.youtube.com</a> and sign in with the Google account for your channel.</li>
<li><b>Verify your phone number:</b> Settings &rarr; Channel &rarr; Feature eligibility &rarr; Intermediate features. You need this for the 48-minute video (longer than 15 minutes) and for custom thumbnails.</li>
<li><b>A day before uploading, turn on Advanced features:</b> on the same page, under Advanced features, click Access features and choose video verification (a short face video on your phone) or your ID. Google usually reviews it within 24 hours and emails you. Until then, the chapters and the links in the descriptions show as plain text; once it is approved they work. If neither option is offered, upload anyway: YouTube turns these features on later as the channel builds history.</li>
<li><b>Channel name:</b> your own name, or danpune to match the links. Nothing that looks like USCIS or a government office (no &ldquo;USCIS&rdquo;, &ldquo;Official&rdquo;, &ldquo;Gov&rdquo;), and no seal, eagle or flag-shield picture.</li>
<li>%s</li>
<li><b>Channel link</b> (works even before Advanced features): on the same Profile page, Links &rarr; Add link. Title: <i>Civics practice with your state's answers</i>. URL: <i>https://danpune.github.io/greencard-checklist/civics.html</i>. Publish.</li>
<li><b>Comments:</b> Settings &rarr; Community moderation &rarr; Content controls. Blocked words: <i>whatsapp, telegram</i>. Link text: On (holds comments with links for review). Save. Immigration videos attract scam comments offering &ldquo;agents&rdquo;.</li>
</ol></section>

<section><h2>2. For each video</h2><ol>
<li>Create &rarr; Upload videos &rarr; choose the video file. Upload <b>full.mp4</b> first. It is about 1.2 GB and can take from a few minutes to over an hour: keep the Mac plugged in with the lid open and the tab open until it says the upload is complete (you can fill in the details meanwhile). If it stops, within 24 hours open youtube.com/upload and choose the same file again; it continues where it left off.</li>
<li><b>Details:</b> paste the title and the description from the video's card below. Thumbnail &rarr; Upload file &rarr; the thumbnail file.</li>
<li><b>Playlists:</b> the first time, Create playlist with the title and description below; after that, pick it.</li>
<li><b>Audience:</b> No, it's not made for kids. Age restriction: No.</li>
<li><b>Show more:</b> Paid promotion (may be called Branded content): No. <b>AI use</b> (may be called Altered content, under Attributes or Show more): <b>No</b> (these are slides; the sound was made from plain tones, not by AI). Tags: paste. Language: English. Caption certification: None. Licence: Standard YouTube License. Category: <b>Education</b>. Comments: On. Comment moderation: Basic.</li>
<li><b>Video elements</b> and <b>Checks</b>: nothing needed. Wait for the copyright check to finish. If it shows a copyright claim, don't delete the video: a claim is not a strike and doesn't hurt your channel. Everything in these videos is public domain, CC0 or made for them, so publish anyway, then go to Studio &rarr; Content &rarr; Restrictions &rarr; Claims &rarr; See details &rarr; Take action &rarr; Dispute, and say you have the rights (the pictures are public domain and the sound is original).</li>
<li><b>Visibility:</b> Public. Or choose Unlisted first, watch it, then make it Public. If YouTube says you have reached a daily limit, upload the rest tomorrow.</li>
</ol>
<p class="muted">Subtitles are not needed: the videos have no speech and every word is on screen. After upload, YouTube shows the video in low quality first; HD can take several hours, longest for the 48-minute video. This is normal: don't delete or re-upload. Chapters appear after processing.</p>
</section>

<section><h2>Playlist</h2>%s%s<p class="muted">Order: all 128, 65/20, practice tests 1, 2, 3.</p></section>

%s

<section><h2>Later</h2><ul>
<li>When the President, Vice President, Speaker or Chief Justice changes, the 128-question and 65/20 videos show old names (the practice tests don't have these questions). The practice site updates its names by itself; then ask Claude: &ldquo;the names changed, remake the full and 65/20 videos&rdquo; (it runs <code>make_slides.py</code>, then <code>make_videos.py full star</code>). YouTube can't swap a video's file: upload each new video with its new description, add it to the playlist, then set the old one to Private.</li>
<li>In early January %d, after the new House elects its Speaker, check <a href="https://www.uscis.gov/citizenship/testupdates">uscis.gov/citizenship/testupdates</a>. If the Speaker changed, remake the full and 65/20 videos (see above). If the 2025 test is still in use, change &ldquo;%d&rdquo; to the new year in the five titles, the five descriptions, the playlist description and the tag &ldquo;citizenship test %d&rdquo; (change <code>IN_USE</code> in make_videos.py and run <code>python3 make_videos.py text</code>). If USCIS announces a new test, retitle or remove the videos.</li>
</ul></section>
</main><script>
function cp(i, b){
  var e = document.getElementById('f' + i), done = function(){ b.textContent = 'Copied'; setTimeout(function(){ b.textContent = 'Copy'; }, 1500); };
  if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(e.value).then(done, function(){ e.select(); document.execCommand('copy'); done(); });
  else { e.select(); document.execCommand('copy'); done(); }
}
</script></body></html>
""" % (field("<b>Channel description</b> (Studio &rarr; Customization &rarr; Profile &rarr; Description)", CHANNEL, 3),
       field("Playlist title", PLAYLIST[0]), field("Playlist description", PLAYLIST[1], 4), "\n".join(cards), IN_USE + 1, IN_USE, IN_USE)

def main():
    args = sys.argv[1:]
    want = [] if args == ["text"] else args or ["full", "star", "test1", "test2", "test3"]
    os.makedirs(OUT, exist_ok=True)
    texts = {}
    for key, plan in plans().items():
        text, chapters, seconds = description(key, plan)
        texts[key] = text
        open(os.path.join(OUT, key + "-description.txt"), "w", encoding="utf-8").write(text)
        print("%s: %d slides, %d chapters, %s, tags %d of 500" % (key, len(plan), chapters, stamp(seconds), tag_length(TAGS[key])))
    open(os.path.join(OUT, "upload.html"), "w", encoding="utf-8").write(upload_page(texts))
    if not want:
        return
    tool = os.path.join(OUT, "video")
    subprocess.run(["swiftc", "-O", "-swift-version", "5", os.path.join(HERE, "Tools", "video.swift"), "-o", tool], check=True, capture_output=True)
    for key, plan in plans().items():
        if key in want:
            json.dump({"slides": [{k: v for k, v in s.items() if k != "chapter"} for s in plan], "sound": True},
                      open(os.path.join(OUT, key + ".plan.json"), "w"))
            subprocess.run([tool, PAGE, os.path.join(OUT, key + ".plan.json"), os.path.join(OUT, key + ".mp4"), os.path.join(OUT, key + "-thumbnail.jpg")], check=True)
            os.remove(os.path.join(OUT, key + ".plan.json"))
    os.remove(tool)

if __name__ == "__main__":
    main()
