#!/bin/sh
# Pack Blender film frames (JPEG, from tools/blender/facility.py --render DIR) into the v2 site's scrub frames.
#   tools/make_film.sh DIR [STEP]
# Needs cwebp (brew install webp) and ffmpeg. Writes src/film/d (1280 px) and src/film/m (640 px) as WebP, keeping every STEP-th frame (default 2),
# plus the five step posters k0..k4.jpg (the key frames used by the static fallback).
set -e
IN=${1:?frames dir}; STEP=${2:-2}; OUT=src/film
rm -rf "$OUT"; mkdir -p "$OUT/d" "$OUT/m"
n=0; i=1
for f in "$IN"/f*.jpg; do
  if [ $(( (i - 1) % STEP )) -eq 0 ]; then
    n=$((n + 1)); name=$(printf "f%03d.webp" $n)
    cwebp -quiet -q 72 -resize 1280 0 "$f" -o "$OUT/d/$name"
    cwebp -quiet -q 70 -resize 640 0 "$f" -o "$OUT/m/$name"
  fi
  i=$((i + 1))
done
k=0
for fr in 34 106 156 212 252; do
  ffmpeg -loglevel error -y -i "$IN/$(printf f%04d.jpg $fr)" -q:v 4 "$OUT/k$k.jpg"; k=$((k + 1))
done
echo "$n frames -> $OUT ($(du -sh "$OUT/d" | cut -f1) desktop, $(du -sh "$OUT/m" | cut -f1) mobile)"
