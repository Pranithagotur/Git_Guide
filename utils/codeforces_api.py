from flask import Blueprint, request, jsonify
import requests

codeforces_api_bp = Blueprint('codeforces_api', __name__, url_prefix='/api')

@codeforces_api_bp.route('/coding_profile')
def get_profile():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400

    info_url = f'https://codeforces.com/api/user.info?handles={username}'
    status_url = f'https://codeforces.com/api/user.status?handle={username}&from=1&count=10000'
    rating_url = f'https://codeforces.com/api/user.rating?handle={username}'

    # Basic info
    user_info = requests.get(info_url).json()
    if user_info['status'] != 'OK':
        return jsonify({'error': 'User not found'}), 404

    user_data = user_info['result'][0]
    solved = set()
    tags = {}

    # Solved problems + tag tracking
    submissions = requests.get(status_url).json()
    if submissions['status'] == 'OK':
        for sub in submissions['result']:
            if sub.get('verdict') == 'OK':
                pid = f"{sub['problem']['contestId']}-{sub['problem']['index']}"
                if pid not in solved:
                    solved.add(pid)
                    for tag in sub['problem'].get('tags', []):
                        tags[tag] = tags.get(tag, 0) + 1

    # Rating history (trend) + recent contests
    rating_history = []
    recent_contests = []
    rating_response = requests.get(rating_url).json()
    if rating_response['status'] == 'OK':
        all_contests = rating_response['result']
        for entry in all_contests:
            rating_history.append({
                'date': entry['ratingUpdateTimeSeconds'],
                'rating': entry['newRating']
            })
            recent_contests.append({
                'name': entry['contestName'],
                'rank': entry['rank'],
                'total': 10000  # placeholder, since CF API doesn't give total participants
            })
        # Convert UNIX timestamps to readable date (optional)
        from datetime import datetime
        for r in rating_history:
            r['date'] = datetime.utcfromtimestamp(r['date']).strftime('%b %d')

    # Recommendations
    def generate_recommendations(tag_stats):
        if not tag_stats:
            return [
                "Solve more problems to unlock insights.",
                "Try a variety of topics to discover your strengths.",
                "Participate in rated contests regularly."
            ]
        weak = sorted(tag_stats.items(), key=lambda x: x[1])[:3]
        recs = [f"Practice more on '{tag}' problems" for tag, _ in weak]
        if len(recs) < 5:
            recs += [
                "Try to participate in at least 2 contests this month.",
                "Review unsolved problems from past contests."
            ]
        return recs[:5]

    return jsonify({
        'handle': user_data.get('handle'),
        'rank': user_data.get('rank'),
        'rating': user_data.get('rating'),
        'maxRank': user_data.get('maxRank'),
        'maxRating': user_data.get('maxRating'),
        'totalSolved': len(solved),
        'tags': [{'name': k, 'count': v} for k, v in tags.items()],
        'recommendations': generate_recommendations(tags),
        'ratingHistory': rating_history,
        'recentContests': recent_contests[:5]
    })
