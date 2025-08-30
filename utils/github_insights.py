import requests
from collections import defaultdict
from utils.github_score import calculate_github_score, generate_ai_recommendations

GITHUB_API = "https://api.github.com/users/{}"
REPOS_API = "https://api.github.com/users/{}/repos"
EVENTS_API = "https://api.github.com/users/{}/events"

def generate_recommendations(profile, languages, activity):
    recommendations = []
    top_language = next(iter(languages), None)
    total_commits = sum(activity.values())
    repo_count = profile.get("repos", 0)
    follower_count = profile.get("followers", 0)

    if top_language:
        recommendations.append(f"Focus more on projects using {top_language}, since it's your most used language.")

    if total_commits < 30:
        recommendations.append("Try to commit more regularly to build a consistent activity graph.")
    else:
        recommendations.append("Great work on staying active! Consider mentoring others or contributing to trending repos.")

    if repo_count < 5:
        recommendations.append("Consider creating more repositories to showcase different projects or experiments.")

    if follower_count < 10:
        recommendations.append("Engage more with the GitHub community to increase your profile visibility.")
    else:
        recommendations.append("You have a healthy follower base! Consider collaborating or publishing developer content.")

    recommendations.append("Improve README and documentation on key repositories to attract more contributors.")

    return recommendations

def get_github_data(username):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "MyGitHubApp",
        "Authorization": "Bearer YOUR_GITHUB_TOKEN_HERE"  # Replace with your GitHub token
    }

    profile_resp = requests.get(GITHUB_API.format(username), headers=headers)
    if profile_resp.status_code != 200:
        return {
            "score": 0,
            "error": "GitHub user not found"
        }
    profile = profile_resp.json()

    repos_resp = requests.get(REPOS_API.format(username), headers=headers)
    repos = repos_resp.json() if repos_resp.status_code == 200 else []

    top_repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:3]
    top_projects = [{
        "name": repo.get("name"),
        "description": repo.get("description") or "No description",
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "language": repo.get("language") or "Unknown",
        "url": repo.get("html_url")
    } for repo in top_repos]

    lang_data = defaultdict(int)
    for repo in repos:
        lang = repo.get("language")
        if lang:
            lang_data[lang] += 1

    events_resp = requests.get(EVENTS_API.format(username), headers=headers)
    events = events_resp.json() if events_resp.status_code == 200 else []
    commit_days = defaultdict(int)
    for event in events:
        if event.get("type") == "PushEvent":
            date = event["created_at"][:10]
            commit_days[date] += 1

    # Build simplified profile
    username = profile.get("login")
    avatar_url = profile.get("avatar_url")
    repo_count = profile.get("public_repos", 0)
    followers = profile.get("followers", 0)

    user_profile = {
        "name": username,
        "repos": repo_count,
        "followers": followers,
        "gists": profile.get("public_gists"),
        "avatar_url": avatar_url,
        "last_active": profile.get("updated_at")[:10] if profile.get("updated_at") else "N/A"
    }

    # Recommendations
    recommendations = generate_recommendations(user_profile, lang_data, commit_days)

    # Scoring
    metrics = {
        "project_quality": 7 if user_profile["repos"] > 3 else 3,
        "code_structure": 6,
        "documentation": 5,
        "contribution_frequency": 8 if len(commit_days) > 20 else 4,
        "tech_stack_diversity": len(lang_data) * 1.5,
        "collaboration": 4,
        "testing_ci": 3,
        "commit_history": 6,
        "github_features": 5,
        "impact_popularity": 7 if user_profile["followers"] > 10 else 3
    }
    github_score = calculate_github_score(metrics)
    ai_recommendations = generate_ai_recommendations(github_score)

    # ✅ Final Flattened Return
    return {
    "github_score": github_score,
    "profile": {
        "name": profile.get("name") or username,
        "login": username,
        "avatar_url": avatar_url,
        "public_repos": repo_count,
        "followers": followers
    },
    "languages": dict(lang_data),
    "commits": dict(commit_days),
    "top_repos": [{
        "name": repo["name"],
        "html_url": repo["url"],
        "stargazers_count": repo["stars"],
        "forks_count": repo["forks"]
    } for repo in top_projects],
    "recommendations": ai_recommendations
}
