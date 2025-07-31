import pytest
import allure
from pages.video_page import VideoPage
from utils.logger import logger


@allure.suite("Edge Case Tests")
@allure.sub_suite("UI + API Behavior")
@pytest.mark.video
@allure.epic("UI edge cases tests")
class TestEdgeCases:

    @pytest.mark.parametrize("action", ["play", "pause"])
    @pytest.mark.parametrize("clicks", [2])
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @allure.title("Double-click '{action}' button keeps video in expected state")
    def test_double_click_play_pause(self, page, action, clicks):
        video = VideoPage(page)
        video.navigate()

        if action == "play":
            with allure.step(f"Double-clicking 'play' button ({clicks} clicks)"):
                for _ in range(clicks):
                    video.play()

            with allure.step("Verify that video is playing"):
                video.wait_until_playing()
                video.assert_is_playing()

        elif action == "pause":
            with allure.step("Start playback before pause"):
                video.play()
                video.wait_until_playing()
                video.assert_is_playing()

            with allure.step(f"Double-clicking 'pause' button ({clicks} clicks)"):
                for _ in range(clicks):
                    video.pause()

            with allure.step("Verify that video is paused"):
                video.wait_until_paused()
                video.assert_is_paused()

        else:
            pytest.fail(f"❌ Unknown action '{action}'")

    @allure.title("Rapid scroll generates multiple scroll events")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("scrolls", [3])
    def test_rapid_scroll_event(self, page, scrolls):
        video = VideoPage(page)
        video.navigate()

        events = []

        def handle_request(request):
            if "/api/event" in request.url:
                data = request.post_data_json
                if data.get("type") == "scroll":
                    events.append(data)

        page.on("request", handle_request)

        with allure.step(f"Scroll {scrolls} times rapidly"):
            for _ in range(scrolls):
                video.scroll()
                page.wait_for_timeout(500)  # short delay between scrolls

        page.remove_listener("request", handle_request)

        assert len(events) >= scrolls, f"❌ Expected {scrolls} scroll events, got {len(events)}"
        logger.info(f"✅ Scroll events captured: {len(events)}")

    @allure.title("Seek to near end of video and validate end state")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.video
    def test_seek_to_end(self, page):
        video = VideoPage(page)
        video.navigate()

        with allure.step("Get video duration"):
            duration = video.get_duration()
            logger.info(f"🎯 Video duration: {duration:.2f} seconds")
            assert duration > 0, "❌ Video duration should be positive"

        with allure.step("Seek to near-end of video (duration - 0.5s)"):
            video.seek(duration - 0.5)
            page.wait_for_timeout(1000)

        with allure.step("Play the video briefly to trigger end"):
            video.play()
            page.wait_for_timeout(2000)

        with allure.step("Assert video ended"):
            is_ended = video.page.evaluate(
                """() => {
                    const video = document.querySelector("#video");
                    return video.ended;
                }"""
            )
            assert is_ended, "❌ Video did not reach ended state"
            logger.info("✅ Video successfully reached ended state")
