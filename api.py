from dotenv import load_dotenv
from dotenv import load_dotenv
load_dotenv()

import os

load_dotenv()
print("OPENAI KEY:", os.getenv("OPENAI_API_KEY"))
