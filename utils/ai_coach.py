import cohere
import os
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def get_ai_suggestions(github_score, leetcode_score, hackerrank_score):
    try:
        prompt = f"""
        You are a placement readiness coach.

        This student has:
        - GitHub Score: {github_score}/100
        - LeetCode Score: {leetcode_score}/100
        - HackerRank Score: {hackerrank_score}/100

        Give 8–10 personalized, short, actionable suggestions to improve their coding profile.
        Base your suggestions on whichever scores are available (non-zero).

        Format:
        - Suggestion 1
        - Suggestion 2
        ...
        """

        response = co.chat(
            model="command-r",
            message=prompt,
            temperature=0.7
        )

        return response.text.strip()

    except Exception as e:
        print("❌ Cohere Error:", e)
        return "Unable to generate suggestions at the moment."
