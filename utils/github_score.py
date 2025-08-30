def calculate_github_score(metrics):
    score = 0
    max_score_per_metric = 10
    total_metrics = 10

    for key in metrics:
        score += min(metrics[key], max_score_per_metric)

    return min(int((score / (max_score_per_metric * total_metrics)) * 100), 100)


def generate_ai_recommendations(score):
    if score >= 85:
        return [
            "Excellent GitHub profile! Keep up the great work.",
            "Consider speaking at events or writing blog posts to boost your visibility.",
            "Collaborate on large-scale or open-source projects for more exposure."
        ]
    elif score >= 70:
        return [
            "Strong profile. Keep contributing regularly and improve project documentation.",
            "Start using GitHub Actions or integrate CI/CD to improve automation.",
            "Increase diversity by exploring different tech stacks and domains."
        ]
    elif score >= 50:
        return [
            "You're on the right track. Try committing more consistently.",
            "Improve README files and provide better documentation.",
            "Engage more with the GitHub community through pull requests or issues."
        ]
    else:
        return [
            "Consider starting more meaningful projects with real-world use cases.",
            "Maintain a consistent commit history and better code structure.",
            "Try collaborating on others’ repositories to gain more experience."
        ]
