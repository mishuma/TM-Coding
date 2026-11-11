"""End-to-end tests for the starter kit, run against index.html opened from file:// (how students run it).

Setup:  pip install playwright pillow && python -m playwright install chromium
Run:    python tests/run_tests.py            (set CHROME=/path/to/chrome to use an installed Chrome)
        KIT=/path/to/unzipped-kit python tests/run_tests.py   (test a packaged release instead of starter/)
Exits non-zero on the first failure.
"""
import asyncio, json, os, shutil, sys, tempfile, zipfile
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
from make_model import build, LABELS

HERE = os.path.dirname(os.path.abspath(__file__))
STARTER = os.environ.get("KIT") or os.path.join(HERE, "..", "starter")
REAL_MODEL = os.path.join(HERE, "fixtures", "real-model")  # a real TM export: dog / cat
CHROME = os.environ.get("CHROME")
ARGS = ["--no-sandbox", "--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"]
HAS_PCT = "document.querySelector('#result').textContent.includes('%')"

def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        sys.exit(1)

async def main():
    work = tempfile.mkdtemp(prefix="tm-starter-test-")
    kit = os.path.join(work, "kit")
    shutil.copytree(STARTER, kit)
    for f in os.listdir(os.path.join(kit, "model")):
        if f != "PUT-MODEL-HERE.txt":
            os.remove(os.path.join(kit, "model", f))
    zpath = await build(work, CHROME)
    loose = os.path.join(work, "loose")
    with zipfile.ZipFile(zpath) as z:
        z.extractall(loose)
    wide = os.path.join(work, "wide.jpg")  # 3:1 photo; only the middle third is yellow/red
    im = Image.new("RGB", (900, 300), "blue"); d = ImageDraw.Draw(im)
    d.rectangle([300, 0, 600, 300], fill="yellow"); d.ellipse([350, 50, 550, 250], fill="red"); im.save(wide)
    bad = os.path.join(work, "notes.txt"); open(bad, "w").write("not a model")
    url = "file://" + os.path.join(kit, "index.html")

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
        ctx = await b.new_context(accept_downloads=True)
        pg = await ctx.new_page()
        page_errors = []
        pg.on("pageerror", lambda e: page_errors.append(str(e)))

        # 1. No saved model -> drop zone; wrong file -> helpful error; zip -> loads
        await pg.goto(url)
        await pg.click("#use-webcam")
        await pg.wait_for_selector(".tmh-overlay")
        check(True, "drop zone appears when no model is saved")
        await pg.set_input_files(".tmh-overlay input", bad)
        await pg.wait_for_selector(".tmh-err:not([hidden])")
        check("Missing" in await pg.inner_text(".tmh-err"), "wrong file shows a 'Missing ...' error")
        await pg.set_input_files(".tmh-overlay input", zpath)
        await pg.wait_for_function(HAS_PCT, timeout=20000)
        check(await pg.locator(".bar-row span").all_inner_texts() == LABELS, "zip loads; one bar per label in model order")
        check(await pg.locator("#webcam canvas").count() == 1, "webcam canvas shown")

        # 2. Save bundle -> reload -> loads without drop zone
        async with pg.expect_download() as dl_info:
            await pg.click(".tmh-banner .tmh-btn:not(.secondary)")
        dl = await dl_info.value
        check(dl.suggested_filename == "model-bundle.js", "save button downloads model-bundle.js")
        await dl.save_as(os.path.join(kit, "model", "model-bundle.js"))
        await pg.reload()
        await pg.click("#use-webcam")
        await pg.wait_for_function(HAS_PCT, timeout=20000)
        check(await pg.locator(".tmh-overlay").count() == 0, "saved bundle loads with no drop zone (file://)")

        # 3. Photo upload: center crop, webcam stops, switching back works
        await pg.set_input_files("#photo", wide)
        await pg.wait_for_selector("#webcam img")
        await pg.wait_for_timeout(500)
        shown = await pg.inner_text("#result")
        await pg.wait_for_timeout(1000)
        check(shown == await pg.inner_text("#result") and "%" in shown, "photo result is not overwritten by the webcam")
        probs = await pg.evaluate("""async () => {
          const img = document.querySelector('#webcam img');
          const c = document.createElement('canvas'); c.width = c.height = 300;
          c.getContext('2d').drawImage(img, 300, 0, 300, 300, 0, 0, 300, 300);
          const truth = (await TM.classify(c)).all.map(x => x.confidence);
          const viaImg = (await TM.classify(img)).all.map(x => x.confidence);
          return {truth, viaImg};
        }""")
        check(all(abs(a - b) < 1e-4 for a, b in zip(probs["truth"], probs["viaImg"])),
              "TM.classify(<img>) uses the true center crop, not a squashed image")
        await pg.click("#use-webcam")
        await pg.wait_for_selector("#webcam canvas")
        check(await pg.locator("#webcam canvas").count() == 1 and await pg.locator("#webcam img").count() == 0,
              "switching back to webcam replaces the photo")

        # 4. Three loose files instead of the zip
        for f in os.listdir(os.path.join(kit, "model")):
            if f.endswith(".js"):
                os.remove(os.path.join(kit, "model", f))
        pg2 = await ctx.new_page()
        await pg2.goto(url)
        await pg2.click("#use-webcam")
        await pg2.wait_for_selector(".tmh-overlay")
        await pg2.set_input_files(".tmh-overlay input", [os.path.join(loose, n) for n in ("model.json", "metadata.json", "weights.bin")])
        await pg2.wait_for_function(HAS_PCT, timeout=20000)
        check(True, "three loose files load")

        check(not page_errors, "no uncaught page errors " + (str(page_errors) if page_errors else ""))
        await b.close()
    # Plain model files served over http load without the drop zone
    shutil.copy(os.path.join(loose, "model.json"), os.path.join(kit, "model"))
    shutil.copy(os.path.join(loose, "metadata.json"), os.path.join(kit, "model"))
    shutil.copy(os.path.join(loose, "weights.bin"), os.path.join(kit, "model"))
    proc = await asyncio.create_subprocess_exec(sys.executable, "-m", "http.server", "8765", cwd=kit,
                                                stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
    await asyncio.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
            pg = await b.new_page()
            await pg.goto("http://localhost:8765/index.html")
            await pg.click("#use-webcam")
            await pg.wait_for_function(HAS_PCT, timeout=20000)
            check(await pg.locator(".tmh-overlay").count() == 0, "served over http: model/ files load with no drop zone")
            await b.close()
    finally:
        proc.terminate()
    await check_real_model(work)
    shutil.rmtree(work, ignore_errors=True)
    print("ALL TESTS PASSED")

async def check_real_model(work):
    """A real Teachable Machine export (tests/fixtures/real-model): zip drop -> save -> reload, on file://."""
    with open(os.path.join(REAL_MODEL, "metadata.json")) as f:
        labels = json.load(f)["labels"]
    zpath = os.path.join(work, "real-tm-model.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for n in ("model.json", "metadata.json", "weights.bin"):
            z.write(os.path.join(REAL_MODEL, n), n)
    kit = os.path.join(work, "real-kit")
    shutil.copytree(STARTER, kit, ignore=shutil.ignore_patterns("model-bundle*.js", "*.zip", "*.bin", "model.json", "metadata.json"))
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
        ctx = await b.new_context(accept_downloads=True)
        pg = await ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        await pg.goto("file://" + os.path.join(kit, "index.html"))
        await pg.click("#use-webcam")
        await pg.set_input_files(".tmh-overlay input", zpath)
        await pg.wait_for_function(HAS_PCT, timeout=60000)
        check(await pg.locator(".bar-row span").all_inner_texts() == labels, "real TM model: zip loads with its labels")
        total = await pg.evaluate("async () => (await TM.classify(document.querySelector('#webcam canvas'))).all.reduce((s, x) => s + x.confidence, 0)")
        check(abs(total - 1) < 1e-3, "real TM model: confidences add up to 100%")
        async with pg.expect_download() as dl_info:
            await pg.click(".tmh-banner .tmh-btn:not(.secondary)")
        await (await dl_info.value).save_as(os.path.join(kit, "model", "model-bundle.js"))
        await pg.reload()
        await pg.click("#use-webcam")
        await pg.wait_for_function(HAS_PCT, timeout=60000)
        check(await pg.locator(".tmh-overlay").count() == 0, "real TM model: ~3 MB saved bundle reloads on file://")
        check(not errors, "real TM model: no uncaught page errors " + (str(errors) if errors else ""))
        await b.close()

asyncio.run(main())
