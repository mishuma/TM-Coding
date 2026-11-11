# Real Teachable Machine model (test fixture)

A real export from Teachable Machine (Image Project, Standard image model, Export, Tensorflow.js), with two classes, `dog` and `cat`. Exported 2026-11-11 by TM 2.4.19 (`tfjsVersion` 1.7.4 in `metadata.json`). The images it was trained on are not included.

`tests/run_tests.py` zips these three files the way TM does, drops the zip on the page, saves `model-bundle.js` and reloads it, all from `file://`. This catches regressions that the small stand-in model from `make_model.py` can't, such as the size of the MobileNet weights and the nested model topology.

Covered by the repository license.
