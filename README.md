This project for position Automation engineer in Minute Media

This project contains UI and API tests

In order to run test locally you need to do the following steps:
1. 🧬Clone GitHub repo.
2. 📦Install all dependencies by running the following command: pip install -r requirements.txt
3. 🧭Ensure headless mode is disabled in conftest.py (line 64)
4. 🧪Open the command prompt in the project root directory and run: $pytest -n 2 --alluredir=reports/allure-results
5. 🧠After the test run completes, you will find results.json under the following path reports/allure-results/
   To analyze the results using **AI**, run $python test/utils/analyze_report_using_ai.py

### 🛰️ Pull Request Automation
Please note that every pull request automatically triggers a full test run.
- The **Allure report** will be generated and a link to it will be printed in the logs (hosted via GitHub Pages).
- The **AI analysis summary** will also appear directly in the pipeline logs.

### 🔮 Future Tasks to Improve the Automation (Ordered by Priority)
1. ✅ **Expand sanity test coverage**  
   Increase the number of sanity tests and create a dedicated job that runs them on every pull request.
2. 🌙 **Nightly full test run**  
   Set up a scheduled job to run the entire test suite nightly for better regression tracking.
3. 🐳 **Create a custom Dockerfile for CI setup**  
   Build a Dockerfile that replicates all installation steps from the current `ci.yml` to ensure consistent local and CI environments.
4. ⚡ **Switch from pip to uv as the dependency manager**  
   Migrate to [`uv`](https://github.com/astral-sh/uv) for faster and more efficient dependency installation and caching.
5. 🧠 **AI test results viewer (Research Task)**  
   Build a GitHub Pages–based frontend to visualize results and insights from the AI analyzer script.
6. 🧪 Run tests in parallel across multiple browsers  
   Execute automated tests concurrently using different browser types (e.g., Chromium, Firefox, WebKit) to ensure full cross-browser coverage.
7. 🎥 Create a GitHub Page to display recorded test videos  
   Build a GitHub Pages–based interface that showcases captured videos from UI test sessions for better debugging and demo visibility.



