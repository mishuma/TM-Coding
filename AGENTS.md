# TM Coding: developer notes for AI agents

This repo builds a **starter kit** that high school students (MIT FutureBuilders / RAISE AI literacy curriculum) use to make an app around an image classifier they trained in Google Teachable Machine (TM). Students "vibe code" their app with an AI assistant, so the kit has to survive being edited by an AI that knows nothing about TM.

You are developing the kit itself, not a student app.

## Two sets of agent instructions: don't mix them up

| File | Audience | Ships to students? |
|---|---|---|
| `AGENTS.md` (this file), `CLAUDE.md` | You, developing the kit | No |
| `starter/AGENTS.md`, `starter/CLAUDE.md` | The student's AI coding assistant | Yes |

The rules in `starter/AGENTS.md` (don't edit `tm-helper.js`, don't touch `lib/`, etc.) apply to **students' AIs**, not to you. You may edit anything in `starter/`. When you change the `TM` API or kit behavior, update `starter/AGENTS.md` and `starter/README.md` to match.

## Layout

```
starter/                 the kit students download (zip this folder)
  index.html             demo app: webcam or photo upload -> label + confidence bars
  tm-helper.js           wrapper around the TM library; exposes global `TM`
  lib/                   vendored @tensorflow/tfjs 1.3.1 + @teachablemachine/image 0.8.5 (from npm)
  model/                 where the student's model-bundle.js goes
  AGENTS.md, CLAUDE.md   instructions for the student's AI
  README.md              student instructions
scripts/
  package.py             zips starter/ -> dist/tm-image-app-starter.zip (what teachers download)
.github/workflows/
  release.yml            on a v* tag: package, run e2e tests on the unzipped zip, attach to a GitHub Release
tests/
  make_model.py          builds a stand-in TM export zip (tiny random net, real TM file format)
  run_tests.py           Playwright end-to-end tests against file://index.html
  fixtures/real-model/   a real TM export (model.json, metadata.json, weights.bin), dog/cat
```

## Hard constraints (the reason the kit exists)

1. **No installs for students.** Opening `starter/index.html` by double-click in Chrome must work. No npm, bundler, server, framework, or CDN dependency.
2. **Works from `file://`.** That's why `tmImage.load(url)` isn't used: it fetches model files, which `file://` blocks. `tm-helper.js` uses `tmImage.loadFromFiles()` with File objects instead, from either (a) `model/model-bundle.js` (a `<script>` that sets `window.TM_MODEL_BUNDLE` with the model files embedded as text/base64), (b) `model/*.json` + `weights.bin` when served over http, or (c) a drop zone for the TM `.zip`. The zip is read with a small built-in parser plus `DecompressionStream('deflate-raw')`.
3. **Pinned library versions.** `@teachablemachine/image@0.8.5` declares a peer dependency on `@tensorflow/tfjs@1.3.1` exactly. Don't upgrade tfjs without testing a real TM model.
4. **Keep it readable by a 15-year-old.** `index.html` is the student's starting point; keep it short with plain comments.

## Known library quirks (already handled in tm-helper.js)

- The library's `cropTo()` reads `img.width` (CSS/rendered size), so an `<img>` shown at a different size gets squashed. `TM.classify` redraws images at natural size first.
- `tmImage.Webcam(w, h, flip=true)` mirrors pixels on its canvas, so predict on `webcam.canvas` with `flipped=false`. The library README's "flip is CSS only" note is wrong for this version.
- `getTotalClasses()` and `getClassLabels()` come from the model and metadata respectively; `metadata.labels` order matches the output order.

## Testing

```
pip install playwright pillow
python -m playwright install chromium
python tests/run_tests.py          # or CHROME=/path/to/chrome python tests/run_tests.py
```

To test the packaged zip instead of `starter/`: `python scripts/package.py && unzip dist/tm-image-app-starter.zip -d /tmp/kit && KIT=/tmp/kit python tests/run_tests.py`.

Uses a fake camera and two models: a tiny **stand-in model** from `make_model.py` for most checks, and a **real TM export** (`tests/fixtures/real-model/`, dog/cat MobileNet) for zip load, the ~3 MB bundle save → reload, and a sanity check of its predictions. Tests: drop zone, bad-file error, zip load, bundle save → reload, center crop, photo vs. webcam switching, three loose files, the http path. Run them after every change.

## Open work (not done yet)

- [x] **Real Teachable Machine export, checked 2026-11-11** with a 2-class (`dog`, `cat`) model exported from TM 2.4.19 (`metadata.tfjsVersion` 1.7.4, `packageVersion` 0.8.4-alpha2). It runs on the vendored tfjs 1.3.1 with no errors or warnings. model.json is 92 KB, weights.bin 2.15 MB (263 tensors, one shard), and `model-bundle.js` 2.98 MB. Bundle on file://, zip drop → save → reload, and loose files over http all work, and the re-saved bundle is byte-identical in size. Headless Chromium on an Apple-silicon Mac: first prediction about 6 s after page load, `TM.classify` median 80–95 ms (WebGL).
- [ ] Still open from that check: (a) time it on a real school laptop or Chromebook; (b) check accuracy on real photos: so far the model has only seen synthetic test images; (c) compare outputs against TM's own preview (tfjs 1.7.4) to confirm 1.3.1 gives the same numbers. The model is committed as `tests/fixtures/real-model/`.
- [ ] Browser checks beyond Chrome: Edge (likely fine), Safari (`file://` webcam permission and `DecompressionStream` support), Chromebook.
- [ ] Windows check: file-picker behavior, and Chrome's `model-bundle (1).js` rename on repeat downloads (the README mentions it; consider detecting it).
- [x] Release packaging: `scripts/package.py` + `.github/workflows/release.yml`. Publish with `git tag vX.Y.Z && git push origin vX.Y.Z`. The zip has no wrapper folder (so Windows "Extract All" doesn't nest folders), and `model/` ships with only `PUT-MODEL-HERE.txt`.
- [ ] Optionally: a teacher guide (lesson flow, sample prompts, common student mistakes), and an example "finished" app to show students.

The repo owner (Jeff, MIT RAISE) decides scope. If something here conflicts with what he asks, his request wins.
