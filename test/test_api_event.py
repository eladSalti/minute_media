import pytest
import requests
import logging
import allure
from datetime import datetime

logger = logging.getLogger(__name__)
BASE_URL = "http://localhost:3000/api/event"


@allure.epic("Backend API Validation")
@allure.feature("POST /api/event")
class TestApiEvent:

    @allure.title("Send valid event and expect 200 OK")
    @allure.step("Sending valid POST /api/event request")
    def test_post_valid_event(self):
        payload = {
            "userId": "user-123",
            "type": "play",
            "videoTime": 12.5,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        response = requests.post(BASE_URL, json=payload)
        logger.info(f"Response status: {response.status_code}, body: {response.text}")
        assert response.status_code == 200

    @allure.title("Send event with missing 'type' field")
    def test_post_missing_type(self):
        payload = {
            "userId": "user-123",
            "videoTime": 12.0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        response = requests.post(BASE_URL, json=payload)
        logger.info(f"Missing 'type' field - Status: {response.status_code}")
        assert response.status_code >= 400, (
            "❗ Expected validation error for missing 'type', "
            f"but got {response.status_code}"
        )

    @allure.title("Send event with wrong data type for videoTime")
    def test_post_invalid_video_time(self):
        payload = {
            "userId": "user-123",
            "type": "pause",
            "videoTime": "not-a-number",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        response = requests.post(BASE_URL, json=payload)
        logger.info(f"Invalid 'videoTime' type - Status: {response.status_code}")
        assert response.status_code >= 400, (
            "❗ Expected validation error for bad 'videoTime', but got "
            f"{response.status_code}"
        )

    @allure.title("Send event with missing 'timestamp' field")
    def test_post_missing_timestamp(self):
        payload = {
            "userId": "user-123",
            "type": "seeked",
            "videoTime": 5.5
        }

        response = requests.post(BASE_URL, json=payload)
        logger.info(f"Missing 'timestamp' - Status: {response.status_code}")
        assert response.status_code >= 400, (
            "❗ Expected validation error for missing 'timestamp', but got "
            f"{response.status_code}"
        )

    @allure.title("Send event with extra unexpected fields")
    def test_post_with_extra_fields(self):
        payload = {
            "userId": "user-123",
            "type": "scroll",
            "videoTime": 6.0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "extra": "not-needed"
        }

        response = requests.post(BASE_URL, json=payload)
        logger.info(f"Payload with extra field - Status: {response.status_code}")
        assert response.status_code == 200

    @allure.title("Send malformed JSON and verify backend handles gracefully")
    def test_malformed_backend_response(self):
        malformed_payload = "{userId: 'abc', type: play}"  # invalid JSON

        response = requests.post(
            BASE_URL,
            headers={"Content-Type": "application/json"},
            data=malformed_payload
        )

        assert response.status_code >= 400, (
            "❌ Expected backend to reject malformed input, but got "
            f"{response.status_code}"
        )

    @allure.title("Send malformed JSON body (not valid JSON at all)")
    def test_post_completely_invalid_json(self):
        malformed_body = "{userId: 123, type: play"  # missing closing }

        response = requests.post(
            BASE_URL,
            data=malformed_body,
            headers={"Content-Type": "application/json"}
        )

        logger.info(f"Malformed JSON payload - Status: {response.status_code}")
        assert response.status_code >= 400, (
            "❗ Expected error for malformed JSON body, but got "
            f"{response.status_code}"
        )

    @allure.title("Send event with missing required fields")
    @pytest.mark.parametrize("missing_field", ["userId", "type", "videoTime", "timestamp"])
    def test_post_missing_fields(self, missing_field):
        payload = {
            "userId": "user-123",
            "type": "scroll",
            "videoTime": 3.2,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        del payload[missing_field]

        response = requests.post(BASE_URL, json=payload)
        logger.info(f"Missing '{missing_field}' - Status: {response.status_code}")
        assert response.status_code >= 400, (
            f"❗ Expected validation error for missing '{missing_field}', "
            f"but got {response.status_code}"
        )

