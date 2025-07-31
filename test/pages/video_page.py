from playwright.sync_api import Page
import allure


class VideoPage:
    def __init__(self, page: Page):
        self.page = page
        self.video_selector = "#video"  # More specific using the element's unique ID

    @allure.step("Navigate to video player page")
    def navigate(self):
        self.page.goto("http://localhost:3000")
        self.page.wait_for_selector(self.video_selector, state="visible")  # Ensure video is loaded

    @allure.step("Play the video using JavaScript")
    def play(self):
        self.page.evaluate(
            """
            () => {
                const video = document.querySelector('#video');
                video.play();
            }
            """
        )
        # Smart wait: instead of a fixed sleep, wait until the video is confirmed to be playing
        # The condition checks that the video is not paused, not ended, and has started progressing in time (currentTime > 0)
        # This ensures the test proceeds only when playback has actually begun
        self.page.wait_for_function(
            """() => {
                const video = document.querySelector('#video');
                return !video.paused && !video.ended && video.currentTime > 0;
            }""",
            timeout=5000  # 5 seconds max
        )

    @allure.step("Pause the video using JavaScript")
    def pause(self):
        self.page.evaluate(
            """
            () => {
                const video = document.querySelector('#video');
                video.pause();
            }
            """
        )

    @allure.step("Seek to {seconds} seconds")
    def seek(self, seconds: float):
        self.page.evaluate(
            f"""
            () => {{
                const video = document.querySelector('#video');
                video.currentTime = {seconds};
            }}
            """
        )

    @allure.step("Scroll the page")
    def scroll(self):
        self.page.mouse.wheel(0, 1000)

    @allure.step("Assert that video is playing")
    def assert_is_playing(self):
        is_playing = self.page.evaluate(
            """
            () => {
                const video = document.querySelector('#video');
                return !video.paused && !video.ended && video.currentTime > 0;
            }
            """
        )
        assert is_playing, "❌ Video is not playing"

    @allure.step("Assert that video is paused")
    def assert_is_paused(self):
        is_paused = self.page.evaluate("""
            () => {
                const video = document.querySelector('video');
                return video.paused === true;
            }
        """)
        assert is_paused, "❌ Video is not paused"

    @allure.step("Assert that video currentTime >= {min_expected} seconds")
    def assert_seek_position(self, min_expected: float):
        current_time = self.page.evaluate("""
            () => {
                const video = document.querySelector('#video');
                return video.currentTime;
            }
        """)
        assert current_time >= min_expected, f"❌ Expected video time >= {min_expected}, but got {current_time}"

    @allure.step("Scroll the page")
    def scroll(self):
        self.page.mouse.wheel(0, 1000)
        self.page.wait_for_timeout(1000)  # give backend time to receive

    @allure.step("Get video duration")
    def get_duration(self) -> float:
        return self.page.evaluate("() => document.querySelector('#video').duration")

    @allure.step("Wait until video is playing")
    def wait_until_playing(self):
        self.page.wait_for_function(
            """() => {
                const video = document.querySelector('#video');
                return !video.paused && !video.ended && video.currentTime > 0;
            }""",
            timeout=5000
        )

    @allure.step("Wait until video is paused")
    def wait_until_paused(self):
        self.page.wait_for_function(
            """() => {
                const video = document.querySelector('#video');
                return video.paused === true;
            }""",
            timeout=5000
        )



