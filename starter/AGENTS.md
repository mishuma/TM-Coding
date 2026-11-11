# Instructions for AI coding assistants

This is a high school student's app that uses an image classification model they trained in Google Teachable Machine. The student is "vibe coding": they describe what they want and you write the code. Keep everything simple enough that the student can read it.

## Hard rules

1. **The app must keep working by double-clicking `index.html`** in Chrome. No web server, no `npm`, no build step, no bundler, no frameworks (React, Vue, etc.), no TypeScript. Plain HTML, CSS and JavaScript only.
2. **Do not install anything.** Do not add `package.json`. Do not add CDN `<script>` tags for TensorFlow.js or Teachable Machine; they are already in `lib/`. Other libraries are discouraged; if one is truly needed, ask the student first.
3. **Do not edit** `tm-helper.js`, anything in `lib/`, or anything in `model/`.
4. **Never open or read `model/model-bundle.js`.** It is a multi-megabyte base64 file containing the student's model. Reading it wastes your context and tells you nothing useful.
5. **Keep these four script tags in `index.html`, in this order, before the app's own script:**
   ```html
   <script src="lib/tf.min.js"></script>
   <script src="lib/teachablemachine-image.min.js"></script>
   <script src="model/model-bundle.js"></script>
   <script src="tm-helper.js"></script>
   ```
   A "file not found" console error for `model/model-bundle.js` is expected until the student saves their model. Do not "fix" it by removing the tag.
6. **Use the `TM` helper API below.** Do not call `tmImage.load`, `tf.loadLayersModel` or `fetch` to load the model, and do not write your own webcam code for classification. The helper already handles loading from a double-clicked file, which plain `tmImage.load` cannot do.
7. Prefer keeping the app in `index.html`. If it grows large, a separate `app.js` / `style.css` next to it is fine.

## TM helper API (global `TM`)

```js
const labels = await TM.loadModel();
// -> ["Class 1", "Class 2", ...] exactly as named in Teachable Machine.
// The first time, this shows a drop zone asking for the model .zip. After the student
// saves model/model-bundle.js, it loads instantly.

await TM.startWebcam('webcam', { size: 300 });
// Puts a mirrored, square webcam view inside the element with id="webcam".
// Needs a user click first (browsers require it), so call it from a button handler.

TM.onPrediction(result => { ... }, { everyMs: 100 });
// Calls your function repeatedly with the latest prediction from the webcam:
//   result.label       "Thumbs up"           (highest-confidence class)
//   result.confidence  0.93                  (0 to 1)
//   result.all         [{ label, confidence }, ...] for every class, in model order

const r = await TM.classify(imgOrCanvasOrVideoElement);
// One-off prediction on an <img>, <canvas> or <video>. Same result shape.
// Uses the square center of the picture, like Teachable Machine does.

TM.stopWebcam();
TM.labels;   // same array loadModel returned
```

## Things that commonly go wrong

- **Label names must match exactly**, including capitals and spaces. Read them from `TM.labels` or `result.all`; don't guess. If the student's code compares to a label, show them the actual labels.
- **Predictions flicker.** The model's top guess can jump between classes on single frames. For anything that triggers an action (play a sound, add a point, change a page), require a confidence threshold (e.g. `> 0.8`) *and* that the same label has held for a short time (e.g. 0.5–1 s) before acting, and add a cooldown so it doesn't fire every frame.
- **`onPrediction` runs ~10 times per second.** Don't create new DOM elements, play sounds, or `alert()` on every call. Update existing elements, and use state variables to fire actions once.
- **Don't flip the image again.** The helper already mirrors the webcam to match how Teachable Machine trained.
- **Square input.** The model sees a square center crop. Keep the webcam size square.
- **Uploaded photos:** the starter page already has this (`classifyPhoto` in `index.html`): `<input type="file" accept="image/*">` → `<img>` with `URL.createObjectURL(file)` → `await TM.classify(img)`. `TM.classify` handles CSS-sized images correctly; do not pass an `<img>` straight to `TM.model.predict`, which squashes it. Call `TM.stopWebcam()` before showing a photo, or the webcam's predictions will overwrite the photo's result.
- **Camera blocked:** if `startWebcam` throws, show `err.message` on the page; it explains how to allow camera access.
- **The model is only as good as its training.** If results are poor, the fix is usually more and more varied training images in Teachable Machine, not more code. Say so.

## Style for this student project

- Short functions with plain names and brief comments a beginner can follow.
- Show the model's current label and confidence somewhere on screen while developing; it helps the student debug.
- After each change, tell the student what to try in the browser to see it working.
