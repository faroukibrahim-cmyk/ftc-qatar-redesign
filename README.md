# FTC Qatar website redesign

The live site is ftc-qatar.com. This repo holds the audit, the v1 design, and two static builds in English and Arabic.

| Path | What |
|---|---|
| `research/` | Audit, full content inventory, reference sites, v2 3D plan, current brochure |
| `design/canvas/` | v1 Claude Design canvas sources (artboards) |
| `src/i18n/{en,ar}.json` | All site copy, one file per language |
| `src/i18n/catalog.json` | Every solution, product line, product, project, About/Services/Contact page, as [English, Arabic] pairs. Items with `"written": true` had no copy on the live site and need FTC sign-off |
| `src/img/p`, `src/img/ref` | Product and project photos from ftc-qatar.com, converted to WebP |
| `src/css`, `src/js`, `src/img` | Shared styles (design tokens), scripts, FTC photos |
| `src/js/v2/` | three.js facility cutaway, scroll film and group globe (v2 only) |
| `tools/blender/facility.py` | The 3D facility: builds it headless, exports `src/models/facility.glb`, renders the film |
| `tools/make_film.sh` | Packs rendered frames into `src/film/` (WebP, desktop + mobile, step posters) |
| `design/3d/ftc-facility.blend` | The same scene saved for a 3D artist to open and refine |
| `tools/build.py` | Builds `dist/v1` and `dist/v2` (stdlib Python, no deps) |

```bash
python3 tools/build.py          # -> dist/v1, dist/v2
python3 -m http.server 8101 --directory dist/v1
```

The **Design options** button on every page switches theme, accent, headline style and corners. "Copy link" shares the chosen look with `?theme=…&accent=…&type=…&shape=…`.

Regenerate the 3D (needs Blender 5.1+, `cwebp`, `ffmpeg`):

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/blender/facility.py -- --glb src/models/facility.glb --blend "$PWD/design/3d/ftc-facility.blend" --render /tmp/ftc-frames --step 2 --w 1920 --h 1080 --samples 64
tools/make_film.sh /tmp/ftc-frames 2
python3 tools/build.py
```
