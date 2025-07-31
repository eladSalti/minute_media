# ✅ Test Plan – MyPlayer Video Web Client

This document summarizes all automated test cases for the MyPlayer video client project.

---

## 🎬 UI Tests – Sanity & Functionality

- ✅ `test_play_video` – Play the video and verify playback starts  
- ✅ `test_pause_video` – Pause the video and verify it pauses  
- ✅ `test_seek_video` – Seek to 10s and confirm position updated  
- ✅ `test_scroll_event` – Scroll page and assert scroll event is sent  

---

## ⚙️ UI Edge Cases

- ✅ `test_double_click_play_pause[action=play, clicks=2]` – Double click play, ensure video is playing  
- ✅ `test_double_click_play_pause[action=pause, clicks=2]` – Double click pause, ensure video is paused  
- ✅ `test_rapid_scroll_event[scrolls=3]` – Scroll 3 times rapidly and expect ≥3 events  
- ✅ `test_seek_to_end` – Seek to end of video and confirm it reaches "ended" state  

---

## 🧪 API Event Tests

- ✅ `test_post_valid_event` – Send valid event and expect 200 OK  
- ✅ `test_post_missing_type` – Omit `type` field and expect 4xx error  
- ✅ `test_post_invalid_video_time` – Send string as `videoTime` and expect 4xx error  
- ✅ `test_post_missing_timestamp` – Omit `timestamp` field and expect 4xx error  
- ✅ `test_post_with_extra_fields` – Add unused fields and expect 200 OK  
- ✅ `test_malformed_backend_response` – Send malformed JSON string and expect rejection  
- ✅ `test_post_completely_invalid_json` – Send invalid JSON body and expect 4xx  
- ✅ `test_post_missing_fields[userId]` – Remove `userId` and expect 4xx  
- ✅ `test_post_missing_fields[type]` – Remove `type` and expect 4xx  
- ✅ `test_post_missing_fields[videoTime]` – Remove `videoTime` and expect 4xx  
- ✅ `test_post_missing_fields[timestamp]` – Remove `timestamp` and expect 4xx  

---

## 📝 Manual Tests

- 🔍 Video loads with no buffering (under varying network conditions)
- 🔍 Ensure no JavaScript errors appear in browser console during interaction  
- 🔍 Validate UI responsiveness under high CPU/memory load
- 🔍 Verify keyboard accessibility and screen reader compatibility (ARIA roles, tab navigation)

---
