# Teachable Machine App Starter

Build an app that uses an image model you trained yourself. Nothing to install: you only need Chrome.

## 1. Train and download your model

1. Go to https://teachablemachine.withgoogle.com → **Get Started** → **Image Project** → **Standard image model**.
2. Name your classes (for example `Thumbs up`, `Thumbs down`, `Nothing`) and add webcam samples for each. Aim for 100+ images per class, with different backgrounds, lighting and angles.
3. Click **Train Model**, and test it in the Preview panel.
4. Click **Export Model** → **Tensorflow.js** tab → **Download my model**. You get a `.zip` file. Leave it zipped.

## 2. Run the starter app

1. Unzip this starter folder somewhere you can find it (e.g. Documents).
2. Double-click `index.html` so it opens in **Chrome**.
3. Click **Use webcam** (or **Upload a photo**), then drop your model `.zip` on the page. Allow the camera when asked.
4. You should see your class names, with bars that move as you change what the camera sees.
5. To test a picture from your laptop instead, click **Upload a photo** or drag an image onto the box. The box shows the square middle part of the photo, which is what the model looks at.

**Do this once:** click **Save model to project**, then move `model-bundle.js` from your Downloads folder into this project's `model` folder. Now your model loads automatically every time you reload.

## 3. Vibe code your app

Open this whole folder in your AI coding tool (Claude, Cursor, Copilot, …). It will read `AGENTS.md`, which explains how to use your model, so you can just describe what you want:

- "When the model sees *Thumbs up* for one second, play a sound and add a point."
- "Turn this into a rock-paper-scissors game against the computer."
- "Add a button to upload a photo and show what the model thinks it is."
- "Make the page look like a retro arcade game."

After each change, reload the page in Chrome to try it.

## If something goes wrong

| Problem | Fix |
|---|---|
| Camera doesn't start | Click the camera icon in Chrome's address bar and allow it. Close Zoom/Meet/other apps using the camera. |
| "That is the Keras download" | Re-export: **Export Model** → **Tensorflow.js** tab → **Download my model**. |
| Page asks for the model every time | You haven't moved `model-bundle.js` into the `model` folder yet (check it's not named `model-bundle (1).js`). |
| Retrained your model | Delete `model/model-bundle.js`, reload, drop the new `.zip`, save again. |
| Predictions are wrong or jumpy | Add more, more varied training images in Teachable Machine and re-export. |

## What's in this folder

| File | What it is | Edit it? |
|---|---|---|
| `index.html` | Your app | Yes |
| `AGENTS.md`, `CLAUDE.md` | Instructions for your AI coding tool | Only if your teacher says so |
| `tm-helper.js` | Loads your model and runs the webcam | No |
| `lib/` | TensorFlow.js 1.3.1 and the Teachable Machine library | No |
| `model/` | Your saved model | No |
