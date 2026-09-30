# Civics Test screensaver for Mac

A screensaver that shows the 128 questions of the 2025 U.S. naturalization civics test, one at a time.
The question is shown for 5 seconds, then the answer with a picture and a short explanation.

**Unofficial.** Not made by USCIS or any government agency. Not legal advice.

This is the 2025 test, for people who file Form N-400 on or after October 20, 2025. If you filed earlier, you take
the 2008 test (100 questions). USCIS.gov is the official source:
[2025 Civics Test](https://www.uscis.gov/citizenship-resource-center/naturalization-test-and-study-resources/2025-civics-test).

Practice the questions, with your own state's answers, at https://danpune.github.io/greencard-checklist/civics.html

## Install

1. Download `Civics-Test-screensaver.zip` from the [latest release](https://github.com/danpune/civics-screensaver/releases/latest) and open it.
2. Double-click `Civics Test.saver`. macOS asks whether to install it for you or for all users.
3. macOS will warn that Apple could not check the screensaver for malware. Open **System Settings → Privacy & Security**, scroll down, and press **Open Anyway**.
4. Choose it as your screen saver:
   - **macOS 26 or later:** System Settings → **Wallpaper** → **Screen Saver…** → scroll to the last group, **Other** → **Show All** → **Civics Test**.
   - **macOS 13 to 15:** System Settings → **Screen Saver** → scroll to **Other** → **Civics Test**.
5. If System Settings says the display sleeps before the screen saver starts, open **Lock Screen** and make
   "Start Screen Saver when inactive" shorter than "Turn display off".

Step 3 is needed once. macOS shows the warning because the screensaver is not notarized: it is not signed with a paid
Apple developer account, so Apple has not checked it
([Apple: Safely open apps on your Mac](https://support.apple.com/en-us/102445)). Go on only if you trust this project.
All the code is in this repository, and you can build it yourself (see below).

If you are comfortable with Terminal, you can run this instead of step 3, before you double-click the file. It removes
the mark that macOS puts on downloaded files (quarantine) from this one file, so macOS does not show the warning:

```bash
xattr -dr com.apple.quarantine ~/Downloads/"Civics Test.saver"
```

Needs macOS 13 or later. Works on Apple silicon and Intel Macs.

To remove it, delete `Civics Test.saver` from `~/Library/Screen Savers`, or from `/Library/Screen Savers` if you
installed it for all users (macOS asks for an administrator password).

## What it shows

- All 128 questions, from USCIS form M-1778 (09/25), in random order. Each answer slide shows up to four accepted
  answers in the official order (five when the question asks for five) and says how many more are accepted. The full
  list is in the official form: see [Sources](#sources).
- Questions that ask for two, three or five answers say so above the answers ("Name two").
- A short "why" for each answer. These notes are not USCIS text: they were written for the practice site, based on
  the USCIS 2025 study guide (see [Sources](#sources)).
- A picture for 127 of the 128 answers (117 different pictures). Every picture is public domain or CC0: see
  [CREDITS.md](CREDITS.md).
- Four questions depend on where you live (senators, representative, governor, capital). The screensaver shows
  "Answers will vary" for them, as the official list does. Look up your own on the practice page above.
- Four questions ask for the name of an office holder: the President, Vice President, Speaker of the House and Chief
  Justice. The slide shows every form of the name that USCIS accepts and the date the names were checked. When the Mac
  is online, the names are refreshed from the practice site, which checks the USCIS test updates page every day.
  Before your interview, check them yourself at [USCIS test updates](https://www.uscis.gov/citizenship/testupdates):
  you must give the name of the person serving at the time of your interview.

## Privacy

The screensaver collects nothing and has no analytics. When the Mac is online it makes one network request each time
it starts: it downloads https://danpune.github.io/greencard-checklist/officials.json, the current names of the four
office holders. That file is hosted on GitHub Pages, so GitHub receives the request and, like any web host, logs the IP
address it came from
([GitHub's note](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection)).
No cookie or identifier is sent. Offline, the screensaver works the same, with the names from the day of the build.

## Sources

- **Questions and accepted answers:** USCIS,
  [128 Civics Questions and Answers (2025 version)](https://www.uscis.gov/sites/default/files/document/questions-and-answers/2025-Civics-Test-128-Questions-and-Answers.pdf),
  form M-1778 (09/25).
- **About the 2025 test:** USCIS,
  [2025 Civics Test](https://www.uscis.gov/citizenship-resource-center/naturalization-test-and-study-resources/2025-civics-test).
- **Names of the four office holders:** USCIS, [Check for Test Updates](https://www.uscis.gov/citizenship/testupdates).
- **Explanations:** written for the practice site, based on USCIS,
  [One Nation, One People: The USCIS 2025 Civics Test Study Guide](https://www.uscis.gov/sites/default/files/document/brochures/USCIS-2025-Civics-Test-Study-Guide.pdf)
  (PDF, 39 MB). For 23 of the 128, where the guide says nothing or is not exact, general history references were also
  used; those 23 are marked `"s": 1` in [why.json](https://github.com/danpune/greencard-checklist/blob/main/why.json).
- **Pictures:** Wikimedia Commons. [CREDITS.md](CREDITS.md) gives each picture's credit, its licence, the reason it is
  free to use, and a link to its source page.

## Build it yourself

Needs the Xcode Command Line Tools, Python 3 with Pillow, and a copy of
[greencard-checklist](https://github.com/danpune/greencard-checklist) next to this folder.

```bash
./build.sh            # writes build/Civics Test.saver
./build.sh install    # builds and copies it to ~/Library/Screen Savers
./build.sh zip        # builds and zips it for a release
swift Tools/preview.swift "build/Civics Test.saver"   # shows it full screen without changing any setting
```

- `slides.html` is the design. `make_slides.py` fills it with the questions and the pictures and writes `web/`.
- `Sources/CivicsSaverView.swift` shows that page full screen.
- `swift Tools/page.swift "$PWD/web/index.html" "q=2&side=a" out.png` saves a picture of one slide.
- `get_pictures.py` downloads the pictures listed in `picks.json` and writes `pictures.json` and `CREDITS.md`.

## Licence

The code is MIT licensed: see [LICENSE](LICENSE). The questions and answers are a work of the U.S. government (USCIS
form M-1778) and are not under copyright in the United States
([17 U.S.C. 105](https://www.law.cornell.edu/uscode/text/17/105)). The pictures are public domain or CC0: see
[CREDITS.md](CREDITS.md). The explanations and picture captions were written for this project and its practice site.

Apple, Mac and macOS are trademarks of Apple Inc., registered in the U.S. and other countries and regions. This project
is not affiliated with, sponsored by or endorsed by Apple Inc.
