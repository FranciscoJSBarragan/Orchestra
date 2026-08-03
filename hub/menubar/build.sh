#!/bin/sh
# Build OrchestraHubMenu.app (no Xcode project, no signing; personal use).
set -eu
cd "$(dirname "$0")"
mkdir -p build
swiftc -O main.swift -o build/OrchestraHubMenu
APP="build/OrchestraHubMenu.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
cp Info.plist "$APP/Contents/Info.plist"
mv build/OrchestraHubMenu "$APP/Contents/MacOS/OrchestraHubMenu"
echo "Built $APP"
