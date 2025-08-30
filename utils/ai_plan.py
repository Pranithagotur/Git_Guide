import os, json, re, cohere
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))
MODEL = "command"

def _ask(prompt, tok=380, temp=0.7):
    for _ in range(2):
        resp = co.generate(model=MODEL, prompt=prompt,
                           max_tokens=tok, temperature=temp)
        text = resp.generations[0].text.strip()
        if "{" in text and "}" in text:
            return text
    raise ValueError("❌ No valid JSON response from Cohere")

def _extract_json(raw):
    m = re.search(r'\{.*\}', raw, re.S)
    if not m:
        raise ValueError("No JSON block")
    return json.loads(m.group(0))

def generate_plan(skill_gaps, strengths, interests):
    gaps = ", ".join(skill_gaps) or "none"
    stren = ", ".join(strengths) or "none"
    intr = ", ".join(interests) or "none"

    prompt = f"""
You are an expert mentor.
Student gaps: {gaps}. Strengths: {stren}. Interests: {intr}.
Reply ONLY in pure JSON with the following structure:

{{
  "ideas": [
    {{
      "title": "string",
      "stack": ["tech1","tech2"],
      "features": ["f1","f2","f3"],
      "blurb": "one sentence"
    }},
    {{…}}, {{…}}
  ],
  "resources": [
    {{ "title": "string", "url": "https://..." }},
    {{…}}
  ],
  "roadmap": ["week1", "week2", "week3", "week4"]
}}
Exactly 3 ideas, ≤6 resources, 4 roadmap bullets.
"""

    raw_text = _ask(prompt, tok=450, temp=0.55)
    try:
        return json.loads(raw_text)
    except:
        return _extract_json(raw_text)
