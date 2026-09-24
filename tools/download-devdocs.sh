#!/bin/sh
# Download a DevDocs topic into the doc-lookup skill.
# Usage: tools/download-devdocs.sh <slug>     e.g. bash, openjdk~8
# Slugs: https://devdocs.io/docs.json ("slug" field)
set -eu

if [ $# -ne 1 ]; then
  echo "usage: $0 <devdocs-slug>   (e.g. bash, openjdk~8)" >&2
  exit 2
fi

slug="$1"
repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
# Folder names avoid "~" (openjdk~8 -> openjdk-8).
topic="$(printf '%s' "$slug" | tr '~' '-')"
dest="$repo_dir/skills/doc-lookup/devdocs/$topic"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

for f in index.json db.json; do
  # -f: fail on HTTP errors instead of saving the error page as data.
  if ! curl -fsSL "https://documents.devdocs.io/$slug/$f" -o "$tmp/$f"; then
    echo "error: could not download $f for '$slug'. Check the slug at https://devdocs.io/docs.json" >&2
    exit 1
  fi
  if ! jq -e . "$tmp/$f" >/dev/null 2>&1; then
    echo "error: $f for '$slug' is not valid JSON" >&2
    exit 1
  fi
done

mkdir -p "$dest"
mv "$tmp/index.json" "$tmp/db.json" "$dest/"
echo "saved $slug to skills/doc-lookup/devdocs/$topic"
