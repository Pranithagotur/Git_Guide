import requests

res = requests.get("https://leetcode.com")
print("Status:", res.status_code)
