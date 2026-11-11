"""Build a tiny stand-in for a Teachable Machine TF.js export (tm-my-image-model.zip).

Same file layout and metadata.json shape as Teachable Machine's "Tensorflow.js -> Download my model",
but a small random network instead of MobileNet, so predictions are arbitrary but deterministic
in shape. Usage: python make_model.py OUT_DIR
"""
import asyncio, base64, json, os, sys, zipfile
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
TF = os.path.join(HERE, "..", "starter", "lib", "tf.min.js")
LABELS = ["Thumbs up", "Thumbs down", "Nothing"]

async def build(out_dir, chrome=None):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=chrome, args=["--no-sandbox"])
        pg = await b.new_page()
        await pg.set_content("<html></html>")
        await pg.add_script_tag(path=TF)
        out = await pg.evaluate("""async () => {
          tf.setBackend('cpu');
          const m = tf.sequential();
          m.add(tf.layers.conv2d({inputShape:[224,224,3],filters:4,kernelSize:3,strides:4,activation:'relu',kernelInitializer:tf.initializers.glorotUniform({seed:1})}));
          m.add(tf.layers.globalAveragePooling2d({}));
          m.add(tf.layers.dense({units:3,activation:'softmax',kernelInitializer:tf.initializers.glorotUniform({seed:2})}));
          let art;
          await m.save(tf.io.withSaveHandler(async a => { art = a; return {modelArtifactsInfo:{dateSaved:new Date(),modelTopologyType:'JSON'}}; }));
          const bytes = new Uint8Array(art.weightData); let s = ''; for (const x of bytes) s += String.fromCharCode(x);
          return {topo: art.modelTopology, specs: art.weightSpecs, w: btoa(s)};
        }""")
        await b.close()
    model = {"modelTopology": out["topo"], "format": "layers-model", "generatedBy": "tests/make_model.py",
             "convertedBy": None, "weightsManifest": [{"paths": ["weights.bin"], "weights": out["specs"]}]}
    meta = {"tfjsVersion": "1.3.1", "tmVersion": "2.4.10", "packageVersion": "0.8.4",
            "packageName": "@teachablemachine/image", "timeStamp": "2026-01-01T00:00:00Z",
            "userMetadata": {}, "modelName": "tm-my-image-model", "labels": LABELS, "imageSize": 224}
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "tm-my-image-model.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("model.json", json.dumps(model))
        z.writestr("metadata.json", json.dumps(meta))
        z.writestr("weights.bin", base64.b64decode(out["w"]))
    return path

if __name__ == "__main__":
    print(asyncio.run(build(sys.argv[1] if len(sys.argv) > 1 else ".", os.environ.get("CHROME"))))
