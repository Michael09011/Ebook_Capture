#!/usr/bin/env sh
set -e
cd "$(dirname "$0")"

# Generate icon assets
python3 icon_generate.py

# Ensure PyInstaller is installed
python3 -m pip install --user pyinstaller

# Clean previous builds
rm -rf build dist __pycache__

# Build a macOS app bundle for the Tkinter GUI
python3 -m PyInstaller \
  --noconfirm \
  --windowed \
  --name "Ebook Capture" \
  --icon ebook_capture.icns \
  --distpath dist \
  --workpath build \
  ebook_capture.py

APP_BUNDLE="dist/Ebook Capture.app"
if [ ! -d "$APP_BUNDLE" ]; then
  APP_BUNDLE="dist/Ebook Capture"
fi
if [ ! -d "$APP_BUNDLE" ]; then
  echo "Error: App bundle not found in dist/"
  exit 1
fi

DMG_PATH="dist/Ebook Capture.dmg"
rm -f "$DMG_PATH"
hdiutil create -volname "Ebook Capture" -srcfolder "$APP_BUNDLE" -ov -format UDZO "$DMG_PATH"

echo "Build complete: dist/Ebook Capture.app"
echo "DMG complete: $DMG_PATH"
