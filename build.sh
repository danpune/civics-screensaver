#!/bin/zsh
# Builds "Civics Test.saver" (universal: Apple silicon + Intel) with only the Xcode Command Line Tools.
#   ./build.sh            build into build/
#   ./build.sh install    build, then copy it to ~/Library/Screen Savers
#   ./build.sh zip        build, then zip it for a GitHub release
#   ./build.sh zip install   both
set -euo pipefail
cd "${0:A:h}"

NAME="Civics Test"
EXE="CivicsSaver"
VERSION="1.1"
MIN_OS="13.0"
OUT="build/$NAME.saver"

rm -rf build && mkdir -p build
python3 make_slides.py   # writes web/ from the questions and the pictures
for arch in arm64 x86_64; do
  swiftc -O -swift-version 5 -parse-as-library -module-name "$EXE" -target "$arch-apple-macos$MIN_OS" \
    -emit-library -Xlinker -bundle -framework ScreenSaver -framework WebKit \
    Sources/*.swift -o "build/$EXE-$arch"
done

mkdir -p "$OUT/Contents/MacOS" "$OUT/Contents/Resources"
lipo -create "build/$EXE-arm64" "build/$EXE-x86_64" -output "$OUT/Contents/MacOS/$EXE"
rm -f build/$EXE-arm64 build/$EXE-x86_64
cp -R web "$OUT/Contents/Resources/web"
cp Resources/thumbnail.png Resources/thumbnail@2x.png "$OUT/Contents/Resources/"   # the small picture in System Settings
cp LICENSE CREDITS.md "$OUT/Contents/Resources/"   # the licence and the picture sources travel with every copy

cat > "$OUT/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>$NAME</string>
  <key>CFBundleDisplayName</key><string>$NAME</string>
  <key>CFBundleIdentifier</key><string>io.github.danpune.civics-screensaver</string>
  <key>CFBundleExecutable</key><string>$EXE</string>
  <key>CFBundlePackageType</key><string>BNDL</string>
  <key>CFBundleShortVersionString</key><string>$VERSION</string>
  <key>CFBundleVersion</key><string>$VERSION</string>
  <key>LSMinimumSystemVersion</key><string>$MIN_OS</string>
  <key>NSPrincipalClass</key><string>CivicsSaverView</string>
  <key>NSHumanReadableCopyright</key><string>Unofficial study aid. Not made by USCIS. Not legal advice. Code: MIT licence. Pictures: public domain in the U.S. or CC0, see CREDITS.md.</string>
</dict></plist>
PLIST

# Ad-hoc signature. Without a paid Apple developer account macOS asks each person to approve it once.
codesign --force --sign - "$OUT"
echo "Built $OUT"

if [[ " $* " == *" zip "* ]]; then
  ditto -c -k --norsrc --keepParent "$OUT" "build/Civics-Test-screensaver.zip"   # no ._ files, so any unzip keeps the signature valid
  shasum -a 256 "build/Civics-Test-screensaver.zip"
fi

if [[ " $* " == *" install "* ]]; then
  mkdir -p "$HOME/Library/Screen Savers"
  rm -rf "$HOME/Library/Screen Savers/$NAME.saver"
  cp -R "$OUT" "$HOME/Library/Screen Savers/"
  echo "Installed. Choose it in System Settings: Wallpaper, Screen Saver..., Other, Show All. On macOS 13 to 15: Screen Saver, Other."
fi
