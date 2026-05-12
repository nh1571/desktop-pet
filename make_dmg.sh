#!/bin/bash
# Build macOS .dmg for Desktop Pet
set -e

NAME="Desktop Pet"
DMG_NAME="Desktop-Pet-macOS.dmg"
DIST_DIR="dist"

echo "=== 1. Generate app icon ==="
python3 generate_icon.py .

echo "=== 2. Build with PyInstaller ==="
rm -rf "$DIST_DIR" build "*.spec"
pyinstaller --onedir --windowed \
    --name "$NAME" \
    --icon app_icon.icns \
    --add-data "LICENSE:." \
    main.py

echo "=== 3. Create .dmg ==="
hdiutil create -volname "$NAME" \
    -srcfolder "$DIST_DIR/$NAME.app" \
    -ov -format UDZO \
    "$DIST_DIR/$DMG_NAME"

echo "=== Done: $DIST_DIR/$DMG_NAME ==="
ls -lh "$DIST_DIR/$DMG_NAME"
