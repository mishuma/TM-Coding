# TM Coding

A no-install starter kit for high school students to build an app around an image model they trained in [Google Teachable Machine](https://teachablemachine.withgoogle.com). It's designed for "vibe coding" with an AI assistant. Part of the MIT FutureBuilders AI literacy curriculum.

- **Students:** download the `starter` folder and follow [`starter/README.md`](starter/README.md).
- **Developers and agents:** see [`AGENTS.md`](AGENTS.md).

## How it works

Students open `starter/index.html` in Chrome by double-clicking it. The first time, they drop in the `.zip` that Teachable Machine exports; one click saves it into the project so later reloads are instant. The page then classifies the webcam or an uploaded photo.

Their AI assistant reads `starter/AGENTS.md`, which describes a small `TM` API (`loadModel`, `startWebcam`, `onPrediction`, `classify`) and the usual mistakes to avoid.

Built on [`@teachablemachine/image`](https://github.com/googlecreativelab/teachablemachine-community/tree/master/libraries/image) 0.8.5 and TensorFlow.js 1.3.1, both vendored in `starter/lib/` (Apache-2.0).

## License

Kit code: MIT (see [`LICENSE`](LICENSE)). Vendored libraries in `starter/lib/`: Apache 2.0 (see [`starter/lib/NOTICE.txt`](starter/lib/NOTICE.txt)).
