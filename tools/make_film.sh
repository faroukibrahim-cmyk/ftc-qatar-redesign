#!/bin/sh
# Pack Blender film frames (JPEG, from tools/blender/facility.py --render DIR --step 2 --w 1920 --h 1080)
# into the v2 site's scrub frames.
#   tools/make_film.sh DIR [STEP]
# Needs cwebp (brew install webp) and ffmpeg. For every STEP-th frame (default 2) it writes WebP:
#   src/film/x  1920x1080  large or high-DPI screens
#   src/film/d  1280x720   other desktops
#   src/film/m  540x810    phones: a centre crop, so portrait screens get native sharpness instead of an upscale
# plus the five step posters k0..k4.jpg (the key frames used by the static fallback).
set -e
IN=${1:?frames dir}; STEP=${2:-2}; OUT=src/film
rm -rf "$OUT"; mkdir -p "$OUT/x" "$OUT/d" "$OUT/m"
n=0; fr=1
while [ $fr -le 270 ]; do
  f="$IN/$(printf f%04d.jpg $fr)"
  n=$((n + 1)); name=$(printf "f%03d.webp" $n)
  cwebp -quiet -q 78 "$f" -o "$OUT/x/$name"
  cwebp -quiet -q 76 -resize 1280 0 "$f" -o "$OUT/d/$name"
  cwebp -quiet -q 72 -crop 600 0 720 1080 -resize 540 810 "$f" -o "$OUT/m/$name"
  fr=$((fr + STEP))
done
k=0
for fr in 34 106 156 212 252; do
  ffmpeg -loglevel error -y -i "$IN/$(printf f%04d.jpg $fr)" -vf scale=1280:-2 -q:v 3 "$OUT/k$k.jpg"; k=$((k + 1))
done
echo "$n frames -> $OUT ($(du -sh "$OUT/x" | cut -f1) 1920, $(du -sh "$OUT/d" | cut -f1) 1280, $(du -sh "$OUT/m" | cut -f1) mobile)"
