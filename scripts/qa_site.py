"""Local browser checks. Uses isolated fixture server; never calls paid speech APIs."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

OUT = Path("artifacts/design-qa")


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results: dict[str, object] = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/opt/google/chrome/chrome",
            args=["--no-sandbox", "--autoplay-policy=user-gesture-required"],
        )
        context = await browser.new_context(viewport={"width": 1440, "height": 1000})
        page = await context.new_page()
        errors: list[str] = []
        failures: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda res: failures.append(res.url) if res.status >= 400 else None)
        await page.goto("http://127.0.0.1:8000")
        await page.locator("#provider-badge").filter(has_text="Demo fixtures").wait_for()
        await page.wait_for_function("currentDraftId !== null")
        await page.select_option("#lang-select", "en-IN")
        await page.wait_for_timeout(400)
        await page.locator("[data-preset=kamla]").click()
        await page.wait_for_function(
            "document.querySelector('#field-person_name').value.length > 0"
        )
        results["sample"] = await page.locator("#field-person_name").input_value()
        results["no_automatic_audio"] = await page.locator("#tts-audio-player").evaluate(
            "(el) => el.paused && !el.src"
        )
        for _ in range(6):
            if await page.locator("#commit-btn").is_enabled():
                break
            await page.locator("#sample-answer-btn").click()
            await page.wait_for_timeout(200)
        await page.locator("#commit-btn").click()
        await page.locator("#committed-result").wait_for(state="visible")
        await page.locator("#view-in-registry-btn").click()
        await page.locator("#registry-table-body tr").first.wait_for()
        results["saved_registry"] = (
            "Kamla" in await page.locator("#registry-table-body").inner_text()
        )
        for selector in ["#export-csv-btn", "#export-json-btn"]:
            async with page.expect_download() as download:
                await page.locator(selector).click()
            results[selector] = (await download.value).suggested_filename
        await page.locator("#tab-registry-btn").focus()
        await page.keyboard.press("ArrowLeft")
        results["workspace_keyboard"] = (
            await page.locator("#tab-form-btn").get_attribute("aria-selected") == "true"
        )
        await page.locator("#stage-speak").focus()
        await page.keyboard.press("ArrowRight")
        results["stage_keyboard"] = await page.locator("#panel-clarify").is_visible()
        await page.keyboard.press("End")
        results["stage_end"] = await page.locator("#panel-review").is_visible()
        await page.locator("#stage-speak").click()
        await page.locator("#particle-mode").click()
        await page.locator("#particle-pause").click()
        results["particle_pause"] = (
            await page.locator("#particle-pause").get_attribute("aria-pressed") == "true"
        )
        for summary in await page.locator("summary").all():
            await summary.focus()
            await page.keyboard.press("Enter")
            assert await summary.evaluate("(el) => el.parentElement.open")
        results["faq_keyboard"] = True
        await page.screenshot(path=str(OUT / "states-success.png"), full_page=True)
        for summary in await page.locator("summary").all():
            await summary.click()
        await page.locator("#new-draft-btn").click()
        await page.wait_for_timeout(300)
        results["reset"] = await page.locator("#field-person_name").input_value() == ""
        # Permission denied in headless context must produce recoverable visible feedback.
        await page.evaluate(
            "() => { navigator.mediaDevices.getUserMedia = async () => { throw new DOMException('Permission denied', 'NotAllowedError'); }; }"
        )
        await page.locator("#record-btn").click()
        await page.wait_for_timeout(500)
        await page.wait_for_function(
            "document.querySelector('#status-message').textContent.includes('Permission denied')"
        )
        results["permission_feedback"] = await page.locator("#status-message").inner_text()
        await page.route(
            "**/api/drafts",
            lambda route: route.fulfill(
                status=503, content_type="application/json", body='{"detail":"Unavailable"}'
            ),
        )
        await page.locator("#new-draft-btn").click()
        await page.wait_for_timeout(200)
        results["error_feedback"] = await page.locator("#status-message").inner_text()
        await page.screenshot(path=str(OUT / "states-error.png"), full_page=True)
        await page.unroute("**/api/drafts")
        await page.emulate_media(reduced_motion="reduce")
        results["reduced_motion"] = await page.locator("#particle-pause").is_disabled()
        await page.screenshot(path=str(OUT / "reduced-motion.png"), full_page=True)
        await page.emulate_media(reduced_motion="no-preference")
        await page.reload()
        await page.wait_for_timeout(400)
        widths = {}
        for width in [320, 360, 390, 768, 1024, 1280, 1440, 1920]:
            await page.set_viewport_size({"width": width, "height": 1000})
            await page.evaluate("scrollTo({top:0,behavior:'instant'})")
            await page.wait_for_timeout(150)
            widths[str(width)] = await page.evaluate(
                "document.documentElement.scrollWidth <= innerWidth"
            )
            await page.screenshot(path=str(OUT / f"{width}.png"), full_page=True)
        results["widths_no_overflow"] = widths
        await page.set_viewport_size({"width": 768, "height": 360})
        results["short_landscape"] = await page.evaluate(
            "document.documentElement.scrollWidth <= innerWidth"
        )
        await page.add_style_tag(content="html { font-size: 200% !important }")
        results["text_zoom_no_overflow"] = await page.evaluate(
            "document.documentElement.scrollWidth <= innerWidth"
        )
        await page.screenshot(path=str(OUT / "text-zoom.png"), full_page=True)
        await context.close()
        static = await browser.new_context(java_script_enabled=False)
        plain = await static.new_page()
        await plain.goto("http://127.0.0.1:8000")
        results["no_js"] = (
            await plain.locator("#hero-title").is_visible()
            and await plain.locator("#panel-review").is_visible()
        )
        await static.close()
        # Browser-level network throttle, cache disabled.
        slow = await browser.new_context()
        slow_page = await slow.new_page()
        session = await slow.new_cdp_session(slow_page)
        await session.send("Network.enable")
        await session.send(
            "Network.emulateNetworkConditions",
            {
                "offline": False,
                "latency": 400,
                "downloadThroughput": 50000,
                "uploadThroughput": 20000,
            },
        )
        await slow_page.goto("http://127.0.0.1:8000", wait_until="domcontentloaded")
        results["slow_network_readable"] = await slow_page.locator("#hero-title").is_visible()
        await slow_page.screenshot(path=str(OUT / "slow-network.png"))
        await browser.close()
        results["page_errors"] = errors
        results["http_failures"] = failures
    (OUT / "browser-results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
