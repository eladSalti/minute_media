import os
import time
import subprocess
import pytest
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)


def wait_for_server(url, timeout=30):
    start = datetime.now()
    for i in range(timeout):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                elapsed = (datetime.now() - start).total_seconds()
                logger.info(f"✅ Server is up after {elapsed:.2f} seconds (attempt {i + 1})")
                return True
        except Exception:
            time.sleep(1)
    logger.error("❌ Server failed to start in time.")
    return False


@pytest.fixture(scope="session", autouse=True)
def start_server(request):
    if not os.environ.get("PYTEST_XDIST_WORKER", "gw0") == "gw0":
        return

    logger.info("🔧 Starting docker-compose...")
    proc = subprocess.Popen(
        ["docker", "compose", "up", "--build"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if not wait_for_server("http://localhost:3000"):
        proc.terminate()
        raise RuntimeError("❌ Server failed to start")

    def fin():
        logger.info("🧹 Shutting down docker-compose...")
        proc.terminate()
        proc.wait()
        logger.info("🛑 Server stopped.")

    request.addfinalizer(fin)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="function")
def page(request):
    with sync_playwright() as p:
        # If you want to run local
        browser = p.firefox.launch(headless=False, slow_mo=500)
        #headless_mode = os.environ.get("CI", "false").lower() == "true"
        #browser = p.firefox.launch(headless=headless_mode, slow_mo=0)
        context = browser.new_context(record_video_dir="videos/")
        page = context.new_page()
        yield page

        video = page.video
        video_path = video.path() if video else None
        context.close()
        browser.close()

        rep_call = getattr(request.node, "rep_call", None)
        if rep_call and rep_call.passed and video_path and os.path.exists(video_path):
            os.remove(video_path)
        elif rep_call and rep_call.failed and video_path:
            logger.info(f"❗ Test failed. Video saved at: {video_path}")