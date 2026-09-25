#!/bin/sh
# Download a DevDocs topic into the doc-lookup skill.
# Usage: tools/download-devdocs.sh <slug>     e.g. bash, openjdk~8
# Slugs: https://devdocs.io/docs.json ("slug" field)
set -eu

if [ $# -ne 1 ]; then
  echo "usage: $0 <devdocs-slug>   (e.g. bash, openjdk~8)" >&2
  exit 2
fi

for cmd in curl jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "error: $cmd is required but not installed (e.g. brew install $cmd, or apt install $cmd)" >&2
    exit 1
  fi
done

slug="$1"
# Slugs are lowercase names, with ~ before a version (openjdk~8). Anything else,
# like a slash or a leading dot, could write outside devdocs/. The letters are
# spelled out because [a-z] also matches capitals in some locales.
case "$slug" in
  '' | .* | *[!abcdefghijklmnopqrstuvwxyz0123456789._~-]*)
    echo "error: '$slug' doesn't look like a DevDocs slug (e.g. bash, openjdk~8)" >&2
    exit 2
    ;;
esac

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
# Folder names avoid "~" (openjdk~8 -> openjdk-8).
topic="$(printf '%s' "$slug" | tr '~' '-')"
dest="$repo_dir/skills/doc-lookup/devdocs/$topic"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
trap 'exit 1' HUP INT TERM

# Look the slug up in the catalog first, so a typo fails before a large
# download, and so meta.json can record which release this is.
if ! curl -fsSL "https://devdocs.io/docs.json" -o "$tmp/docs.json"; then
  echo "error: could not download the DevDocs catalog (https://devdocs.io/docs.json); check the network" >&2
  exit 1
fi
if ! jq -e --arg s "$slug" 'any(.[]; .slug == $s)' "$tmp/docs.json" >/dev/null; then
  echo "error: DevDocs has no topic '$slug'. Slugs are the \"slug\" field in https://devdocs.io/docs.json" >&2
  exit 1
fi

for f in index.json db.json; do
  # -f: fail on HTTP errors instead of saving the error page as data.
  if ! curl -fsSL "https://documents.devdocs.io/$slug/$f" -o "$tmp/$f"; then
    echo "error: could not download $f for '$slug'" >&2
    exit 1
  fi
  if ! jq -e . "$tmp/$f" >/dev/null 2>&1; then
    echo "error: $f for '$slug' is not valid JSON" >&2
    exit 1
  fi
done

# Name, release, and download date, shown by the skill's scripts/devdocs.py.
jq --arg s "$slug" --arg d "$(date -u +%Y-%m-%d)" \
  'first(.[] | select(.slug == $s)) | {name, slug, release, mtime, downloaded: $d}' \
  "$tmp/docs.json" > "$tmp/meta.json"

mkdir -p "$dest"
mv "$tmp/index.json" "$tmp/db.json" "$tmp/meta.json" "$dest/"
echo "saved $slug to skills/doc-lookup/devdocs/$topic"
