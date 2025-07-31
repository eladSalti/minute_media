import pytest
import allure
import logging
from pages.video_page import VideoPage

logger = logging.getLogger(__name__)


@allure.epic("Sanity Test Suite")
@pytest.mark.sanity
class TestVideoSanity:
    """
    This class it's a sanity test suite which can run as part of the CI/CD pipeline,
    and check the following: play, pause, seek and scroll.
    """

    @allure.title("Play video and verify it starts playing")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_play_video(self, page):
        video = VideoPage(page)
        video.navigate()
        video.play()
        video.assert_is_playing()

    @allure.title("Pause video and verify it is paused")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_pause_video(self, page):
        video = VideoPage(page)
        video.navigate()
        video.play()
        video.pause()
        video.assert_is_paused()

    @allure.title("Seek video to 10 seconds and verify position")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_seek_video(self, page):
        video = VideoPage(page)
        video.navigate()
        video.seek(10)  # Seek to 10 seconds
        video.assert_seek_position(min_expected=9)

    @allure.title("Scroll page and verify scroll event is captured")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_scroll_event(self, page):
        video = VideoPage(page)
        video.navigate()

        events = []

        def handle_request(request):
            if "/api/event" in request.url:
                json_data = request.post_data_json
                if json_data.get("type") == "scroll":
                    events.append(json_data)

        page.on("request", handle_request)
        video.scroll()
        page.wait_for_timeout(2000)
        page.remove_listener("request", handle_request)

        assert events, "❌ No scroll event was captured"
        logger.info(f"✅ Scroll event captured: {events[0]}")
