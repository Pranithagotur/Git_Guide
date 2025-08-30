# utils/codechef.py
import requests
from bs4 import BeautifulSoup

def get_codechef_data(username):
    url = f"https://www.codechef.com/users/{username}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {"error": "CodeChef user not found"}

    soup = BeautifulSoup(res.text, "html.parser")

    try:
        rating = soup.select_one(".rating-number").text.strip()
        stars = soup.select_one(".rating-star").text.strip()
        fully_solved = soup.find("section", class_="rating-data-section problems-solved")\
            .find("h5").text.strip().split()[2]
    except Exception:
        return {"error": "Error parsing CodeChef profile"}

    return {
        "username": username,
        "rating": rating,
        "stars": stars,
        "solved": fully_solved
    }
