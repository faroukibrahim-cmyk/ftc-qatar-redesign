# FTC Qatar website redesign

The live site is ftc-qatar.com. This repo holds the audit, the v1 design, and two static builds in English and Arabic.

| Path | What |
|---|---|
| `research/` | Audit, full content inventory, reference sites, v2 3D plan, current brochure |
| `design/canvas/` | v1 Claude Design canvas sources (artboards) |
| `src/i18n/{en,ar}.json` | All site copy, one file per language |
| `src/css`, `src/js`, `src/img` | Shared styles (design tokens), scripts, FTC photos |
| `src/js/v2/` | three.js facility cutaway and group globe (v2 only) |
| `tools/build.py` | Builds `dist/v1` and `dist/v2` (stdlib Python, no deps) |

```bash
python3 tools/build.py          # -> dist/v1, dist/v2
python3 -m http.server 8101 --directory dist/v1
```

The **Design options** button on every page switches theme, accent, headline style and corners. "Copy link" shares the chosen look with `?theme=…&accent=…&type=…&shape=…`.
