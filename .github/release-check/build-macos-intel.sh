#!/bin/bash
# Run on an Intel Mac with Go >= 1.25, pnpm, Python 3 and Command Line Tools.
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
output=${1:?Usage: build-macos-intel.sh OUTPUT_DIRECTORY}
mkdir -p "$output"
output=$(cd "$output" && pwd)
export MACOSX_DEPLOYMENT_TARGET=15.0
export CGO_ENABLED=1 GOOS=darwin GOARCH=amd64
export CC="$(xcrun --find clang) -arch x86_64"
export SDKROOT=$(xcrun --sdk macosx --show-sdk-path)
export CGO_CFLAGS="${CGO_CFLAGS:-} -mmacosx-version-min=$MACOSX_DEPLOYMENT_TARGET"
export CGO_LDFLAGS="${CGO_LDFLAGS:-} -mmacosx-version-min=$MACOSX_DEPLOYMENT_TARGET"
cd "$root/bridge/web"
pnpm install --frozen-lockfile --ignore-scripts
pnpm run build
cd "$root/bridge"
make hubsrc
commit=$(git rev-parse --short HEAD)
version=dev-macos15-intel-$commit
package_tag=$(git describe --tags --abbrev=0 --match 'v[0-9]*')
built=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
go build -trimpath -tags goolm \
  -ldflags "-s -w -X main.version=$version -X main.commit=$commit -X main.buildTime=$built" \
  -o "$output/bothouse" ./cmd/cc-connect
codesign --force --sign - --identifier ai.bothouse.desktop "$output/bothouse"
python3 "$root/.github/release-check/verify-macos-minimum.py" "$output/bothouse" x86_64 15.0
"$output/bothouse" --version
bash "$root/.github/release-check/package-dmg.sh" "$output/bothouse" \
  "$output/bothouse-macos15-intel.dmg" "$package_tag" x86_64 15.0
cd "$output"
shasum -a 256 bothouse bothouse-macos15-intel.dmg > SHA256SUMS
