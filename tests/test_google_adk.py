import unittest

# Marked as "necessary building blocks" for 5 Days of AI notebooks
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

class TestGoogleADK(unittest.TestCase):

    # From "Day 1a - From Prompt to Action"
    def test_define_agent(self):

        retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1, # Initial delay before first retry (in seconds)
            http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
        )

        root_agent = Agent(
            name="helpful_assistant",
            model=Gemini(
                model="gemini-2.5-flash-lite",
                retry_options=retry_config
            ),
            description="A simple agent that can answer general questions.",
            instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
            tools=[google_search],
        )
