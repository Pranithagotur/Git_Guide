import cohere
co = cohere.Client("your_cohere_api_key_here")  # Use your actual API key
res = co.generate(model="command", prompt="Suggest a project for a Python learner", max_tokens=50)
print(res.generations[0].text)
