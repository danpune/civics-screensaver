# Civics Test screensaver for Mac

A screensaver that shows the 128 questions of the 2025 U.S. naturalization civics test, one at a time.
The question is shown for 5 seconds, then the answer with a picture and a short explanation.

**Unofficial.** Not made by USCIS or any government agency. Not legal advice.
Practice the questions at https://danpune.github.io/greencard-checklist/civics.html

## Install

1. Download `Civics-Test-screensaver.zip` from the [latest release](https://github.com/danpune/civics-screensaver/releases/latest) and open it.
2. Double-click `Civics Test.saver`. macOS asks whether to install it for you or for all users.
3. macOS will say it cannot check the screensaver. Open **System Settings → Privacy & Security**, scroll down, and press **Open Anyway**.
4. Open **System Settings → Screen Saver**, scroll to **Other**, and choose **Civics Test**.

Step 3 is needed once. The screensaver is not signed with a paid Apple developer account.
Needs macOS 13 or later. Works on Apple silicon and Intel Macs.

To remove it, delete `Civics Test.saver` from `~/Library/Screen Savers`.

## What it shows

- All 128 questions and accepted answers, from USCIS form M-1778 (09/25), in random order.
- A short "why" for each answer, based on the USCIS 2025 Civics Test Study Guide.
- A picture for most answers. Every picture is public domain or CC0: see [CREDITS.md](CREDITS.md).
- For questions that ask for two, three or five answers, that many are shown.
- Four questions depend on your state (senators, representative, governor, capital). The screensaver shows
  "Answers will vary" for them. Look up your own on the practice page above.
- The names of the President, Vice President, Speaker of the House and Chief Justice are refreshed from the
  practice site when the Mac is online. Offline, the names from the day of the build are shown.

## Privacy

The screensaver collects nothing. Its only network request is for the list of current office holders.

## Build it yourself

Needs the Xcode Command Line Tools, Python 3 with Pillow, and a copy of
[greencard-checklist](https://github.com/danpune/greencard-checklist) next to this folder.

```bash
./build.sh            # writes build/Civics Test.saver
./build.sh install    # builds and copies it to ~/Library/Screen Savers
./build.sh zip        # builds and zips it for a release
```

- `slides.html` is the design. `make_slides.py` fills it with the questions and the pictures and writes `web/`.
- `Sources/CivicsSaverView.swift` shows that page full screen.
- `swift Tools/page.swift "$PWD/web/index.html" "q=2&side=a" out.png` saves a picture of one slide.
- `get_pictures.py` downloads the pictures listed in a checked list and writes `pictures.json` and `CREDITS.md`.

## Licence

The code is MIT licensed. The questions and answers are a U.S. government work. The pictures are public domain or CC0.
