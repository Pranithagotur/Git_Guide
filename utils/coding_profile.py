import requests

def compute_leetcode_score(solved_total: int, ranking: int, easy: int, medium: int, hard: int) -> int:
    total_score = min(solved_total, 600) / 600 * 50
    difficulty_score = 10 if medium > easy else 0
    difficulty_score += 10 if hard >= 10 else 0

    if ranking < 10000:
        rank_score = 20
    elif ranking < 25000:
        rank_score = 15
    elif ranking < 50000:
        rank_score = 10
    else:
        rank_score = 5

    bonus = 10 if medium > 20 or hard > 5 else 5
    final_score = total_score + difficulty_score + rank_score + bonus
    return int(round(min(final_score, 100)))

def get_leetcode_ai_recommendations(score):
    if score >= 85:
        return "Excellent! You are contest-ready. Keep participating and refining speed."
    elif score >= 65:
        return "Great job! Focus on solving more hard problems and improving speed."
    elif score >= 45:
        return "You're doing well. Try participating in rated contests and improve medium questions."
    else:
        return "Start with easier problems, build consistency, and participate in weekly contests."

def get_user_data(username):
    query = {
        "operationName": "getUserProfile",
        "variables": {"username": username},
        "query": """
        query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            username
            profile {
              realName
              ranking
              userAvatar
              reputation
              starRating
            }
            submitStats {
              acSubmissionNum {
                difficulty
                count
                submissions
              }
            }
          }
          recentSubmissionList(username: $username) {
            title
            timestamp
          }
        }
        """
    }

    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/",
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.post("https://leetcode.com/graphql", json=query, headers=headers)

    if res.status_code != 200:
        print("❌ Request failed with status:", res.status_code)
        return None

    json_data = res.json()
    data = json_data.get("data", {})
    matched = data.get("matchedUser")
    recent = data.get("recentSubmissionList", [])

    if not matched:
        print("❌ matchedUser not found")
        return None

    profile = matched.get("profile", {})
    stats = matched.get("submitStats", {}).get("acSubmissionNum", [])

    solved = {
        "easy": next((x["count"] for x in stats if x["difficulty"] == "Easy"), 0),
        "medium": next((x["count"] for x in stats if x["difficulty"] == "Medium"), 0),
        "hard": next((x["count"] for x in stats if x["difficulty"] == "Hard"), 0),
        "total": next((x["count"] for x in stats if x["difficulty"] == "All"), 0),
    }

    ranking = int(profile.get("ranking", 999999))
    score = compute_leetcode_score(
        solved["total"], ranking, solved["easy"], solved["medium"], solved["hard"]
    )

    return {
        "username": matched["username"],
        "realName": profile.get("realName", ""),
        "ranking": ranking,
        "avatar": profile.get("userAvatar", ""),
        "reputation": profile.get("reputation", 0),
        "solved": solved,
        "score": score,
        "ai_recommendation": get_leetcode_ai_recommendations(score),
        "recent": recent[:7]  # last 7 submissions for weekly tracker
    }


if __name__ == "__main__":
    user_data = get_user_data("username")
    print(user_data)
