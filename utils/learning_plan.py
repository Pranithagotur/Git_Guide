import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_learning_plan(github_score, leetcode_score, hackerrank_score):
    prompt = f"""
    Based on these scores:
    - GitHub: {github_score}/100
    - LeetCode: {leetcode_score}/100
    - HackerRank: {hackerrank_score}/100

    Create a 4-week structured learning plan to improve coding and placement readiness.
    For each week, include:
    - Goals
    - Specific tasks (with tools or platforms)
    - Optional links to resources (if known)

    Be motivating, beginner-friendly, and practical.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful AI career mentor for engineering students."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    return response['choices'][0]['message']['content']
