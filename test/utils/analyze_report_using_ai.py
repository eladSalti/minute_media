import os
import json
import pandas as pd
import google.generativeai as genai
from pathlib import Path
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
LOGGER = logging.getLogger(__name__)

# --- Global Path Variables (No direct 'import config' here) ---
script_dir = Path(__file__).resolve().parent  # Path to test/utils/ (assuming script is here)
# CORRECTED: project_root needs to go up 2 levels from 'test/utils/' to the project root
project_root = script_dir.parent.parent  # Path to my_automation_project/ (root)


class AllureReportAnalyzer:
    # CORRECTED: Default reports_path and videos_path should reflect 'test/'
    def __init__(self, reports_path="../reports/allure-results",
                 videos_path="../videos"):
        """
        Initializes the report analyzer with LLM capabilities.
        :param reports_path: Relative path from test/utils/ to the Allure results directory.
                             Example: "../reports/allure-results"
        :param videos_path: Relative path from test/utils/ to the videos directory.
                             Example: "../videos"
        """
        self.reports_path = reports_path
        self.videos_path_relative_to_script = videos_path
        self.full_videos_path = self._resolve_videos_path()

        self.test_results = []
        self.df_results = pd.DataFrame()

        self.llm_model = None

        # --- Logic to load API Key ---
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            try:
                if 'config' not in sys.modules:
                    if str(project_root) not in sys.path:
                        sys.path.insert(0, str(project_root))
                    import config as local_config
                else:
                    local_config = sys.modules['config']

                api_key = getattr(local_config, 'GOOGLE_API_KEY', None)
                if api_key == "YOUR_GEMINI_API_KEY_HERE":
                    api_key = None
            except ImportError:
                LOGGER.info("Warning: 'config.py' not found for local API key loading. This is expected in CI/CD.")
                api_key = None
            except Exception as e:
                LOGGER.info(f"Warning: Error reading GOOGLE_API_KEY from config.py: {e}")
                api_key = None
            finally:
                if 'config' not in sys.modules and str(project_root) in sys.path:
                    sys.path.remove(str(project_root))
        # --- End API Key Logic ---

        # Final check for API key and LLM initialization
        if not api_key:
            LOGGER.info(
                "ERROR: GOOGLE_API_KEY not found in environment variables or config.py. LLM features will NOT be available.")
        else:
            try:
                genai.configure(api_key=api_key)

                available_models = [
                    m.name for m in genai.list_models()
                    if 'generateContent' in m.supported_generation_methods
                ]

                if "models/gemini-pro" in available_models:
                    self.llm_model = genai.GenerativeModel('gemini-pro')
                    LOGGER.info("LLM model 'gemini-pro' initialized successfully.")
                elif available_models:
                    recommended_model = available_models[0]
                    self.llm_model = genai.GenerativeModel(recommended_model)
                    LOGGER.info(
                        f"LLM model 'gemini-pro' not directly available. Initialized with '{recommended_model}'.")
                else:
                    LOGGER.info(
                        "ERROR: No LLM models supporting 'generateContent' found with this API key/region. LLM features will NOT be available.")
                    self.llm_model = None

            except Exception as e:
                LOGGER.info(
                    f"ERROR: Failed to initialize LLM model due to an API error: {e}. LLM features will NOT be available.")
                self.llm_model = None

    def _resolve_videos_path(self):
        """Resolves the absolute path to the videos directory."""
        return os.path.abspath(os.path.join(os.path.dirname(__file__), self.videos_path_relative_to_script))

    def _find_video_for_test_by_uuid(self, test_uuid):
        """
        Attempts to find a video file associated with a test UUID in the videos directory.
        Assumes video files are named using the test's UUID (or contain it).
        :param test_uuid: The UUID of the test.
        :return: Full path to the video file if found, otherwise None.
        """
        if not os.path.exists(self.full_videos_path):
            return None

        for filename in os.listdir(self.full_videos_path):
            if filename.endswith(('.webm', '.mp4', '.avi', '.mov')):
                if test_uuid in filename:
                    return os.path.join(self.full_videos_path, filename)

        return None

    def load_allure_results(self):
        """
        Loads all *-result.json files from the specified reports directory,
        extracts relevant data, and attempts to link associated video files.
        """
        full_reports_path = os.path.abspath(os.path.join(os.path.dirname(__file__), self.reports_path))
        LOGGER.info(f"Searching for Allure result files in: {full_reports_path}")

        if not os.path.exists(full_reports_path):
            LOGGER.info(f"Error: The reports path '{full_reports_path}' does not exist. Please ensure it's correct.")
            return

        found_files = False
        for filename in os.listdir(full_reports_path):
            if filename.endswith("-result.json"):
                found_files = True
                filepath = os.path.join(full_reports_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    test_name = data.get('name', 'N/A')
                    status = data.get('status', 'unknown')
                    start_time_ms = data.get('start')
                    stop_time_ms = data.get('stop')
                    description = data.get('description', '')
                    error_message = None
                    test_uuid = data.get('uuid', 'N/A')

                    duration_seconds = 0
                    if start_time_ms is not None and stop_time_ms is not None:
                        duration_seconds = (stop_time_ms - start_time_ms) / 1000.0

                    if status == 'failed':
                        if 'statusDetails' in data:
                            if 'message' in data['statusDetails']:
                                error_message = data['statusDetails']['message']
                            elif 'trace' in data['statusDetails']:
                                error_message = data['statusDetails']['trace'].split('\n')[0]

                    labels = {label['name']: label['value'] for label in data.get('labels', [])}
                    epic = labels.get('epic', 'N/A')
                    feature = labels.get('feature', 'N/A')
                    suite = labels.get('suite', 'N/A')
                    sub_suite = labels.get('subSuite', 'N/A')
                    test_case_id = data.get('testCaseId', 'N/A')

                    video_path = self._find_video_for_test_by_uuid(test_uuid)

                    self.test_results.append({
                        'test_name': test_name,
                        'status': status,
                        'duration_seconds': duration_seconds,
                        'description': description,
                        'error_message': error_message,
                        'epic': epic,
                        'feature': feature,
                        'suite': suite,
                        'sub_suite': sub_suite,
                        'test_case_id': test_case_id,
                        'uuid': test_uuid,
                        'video_path': video_path
                    })
                except json.JSONDecodeError as e:
                    LOGGER.info(f"Error decoding JSON from {filepath}: {e}")
                except Exception as e:
                    LOGGER.info(f"An unexpected error occurred while processing {filepath}: {e}")

        if not found_files:
            LOGGER.info(
                f"No '-result.json' files found in '{full_reports_path}'. Please ensure your Allure reports are generated there.")

        self.df_results = pd.DataFrame(self.test_results)
        LOGGER.info(f"Loaded {len(self.df_results)} test results.")

    def analyze_summary(self):
        """
        Performs a basic statistical analysis of the test results and returns a summary string.
        """
        if self.df_results.empty:
            return "No test results to analyze."

        total_tests = len(self.df_results)
        passed_tests = self.df_results[self.df_results['status'] == 'passed'].shape[0]
        failed_tests = self.df_results[self.df_results['status'] == 'failed'].shape[0]
        skipped_tests = self.df_results[self.df_results['status'] == 'skipped'].shape[0]

        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        summary = f"""
        --- Automation Report Summary ---
        Total Tests: {total_tests}
        Passed: {passed_tests}
        Failed: {failed_tests}
        Skipped: {skipped_tests}
        Pass Rate: {pass_rate:.2f}%
        ---------------------------------
        """
        return summary

    def get_failed_tests_details(self):
        """
        Returns a detailed string of information for all failed tests, including video links.
        """
        failed_df = self.df_results[self.df_results['status'] == 'failed']
        if failed_df.empty:
            return "No failed tests found in this report."

        details = "--- Failed Tests Details ---\n"
        for index, row in failed_df.iterrows():
            details += f"Test Name: {row['test_name']}\n"
            details += f"Suite: {row['suite']} -> {row['sub_suite']}\n"
            if row['error_message']:
                details += f"Error Message: {row['error_message']}\n"
            details += f"Duration: {row['duration_seconds']:.2f} seconds\n"
            if row['video_path']:
                details += f"Video Link: file:///{row['video_path'].replace(os.sep, '/')}\n"
            details += "----------------------------\n"
        return details

    def get_llm_insights(self, text_to_analyze,
                         prompt_instruction="Analyze the following text and provide key insights and possible recommendations:"):
        """
        Uses an LLM model to get deeper insights from test descriptions or error messages.
        :param text_to_analyze: The text (e.g., error message, test description) to send to the LLM.
        :param prompt_instruction: Specific instructions for the LLM.
        :return: LLM response text or an error message if LLM is not available or call fails.
        """
        if self.llm_model is None:
            return "LLM model is not initialized. Please ensure GOOGLE_API_KEY is correctly set in config.py."

        try:
            full_prompt = f"{prompt_instruction}\n\nText: {text_to_analyze}"
            response = self.llm_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error accessing the LLM model: {e}"

    def analyze_failures_with_llm(self):
        """
        Analyzes error messages of failed tests using the LLM and provides aggregated insights.
        """
        if self.llm_model is None:
            return "LLM model is not initialized. Cannot analyze failures with LLM."

        failed_df = self.df_results[self.df_results['status'] == 'failed']
        if failed_df.empty:
            return "No failed tests to analyze with LLM."

        all_failure_messages = failed_df['error_message'].dropna().unique().tolist()
        if not all_failure_messages:
            return "No specific error messages found in failed tests for LLM analysis."

        combined_text = "\n".join(all_failure_messages)
        LOGGER.info("\n--- LLM Analysis of Failures ---")
        prompt_instruction = (
            "Given the following error messages from failed automation tests, "
            "identify common patterns, suggest potential root causes, and recommend actionable steps to investigate or fix:"
        )
        return self.get_llm_insights(combined_text, prompt_instruction)

    def get_llm_insight_for_specific_test(self, test_name):
        """
        Gets LLM insights for a specific test based on its description and error message (if failed).
        """
        if self.llm_model is None:
            return "LLM model is not initialized. Cannot get specific test insights."

        test_data = self.df_results[self.df_results['test_name'] == test_name]
        if test_data.empty:
            return f"Test '{test_name}' not found in the report."

        test_row = test_data.iloc[0]

        analysis_text = f"Test Name: {test_row['test_name']}\nStatus: {test_row['status']}\nDescription: {test_row['description']}\n"
        if test_row['error_message']:
            analysis_text += f"Error Message: {test_row['error_message']}\n"
        if test_row['video_path']:
            analysis_text += f"Associated Video: {test_row['video_path']}\n"

        prompt_instruction = (
            f"Analyze the following details for a test case '{test_row['test_name']}'. "
            "Provide insights into its status, potential reasons for failure (if applicable), "
            "and suggest next steps for debugging or improvement:"
        )
        LOGGER.info(f"\n--- LLM Insight for Test: {test_name} ---")
        return self.get_llm_insights(analysis_text, prompt_instruction)


# --- How to Use (Main execution block) ---
if __name__ == "__main__":
    analyzer = AllureReportAnalyzer(
        reports_path="../reports/allure-results",
        videos_path="../videos"
    )

    analyzer.load_allure_results()

    summary = analyzer.analyze_summary()
    LOGGER.info(summary)

    failed_details = analyzer.get_failed_tests_details()
    LOGGER.info(failed_details)

    if analyzer.llm_model:
        llm_failure_analysis_output = analyzer.analyze_failures_with_llm()
        LOGGER.info(llm_failure_analysis_output)

        specific_failed_test_name = "Seek to near end of video and validate end state"