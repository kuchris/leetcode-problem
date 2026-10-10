import json
import urllib.request

URL = 'https://leetcode.com/api/problems/all/'
request = urllib.request.Request(
    URL,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/140.0 Safari/537.36',
        'Accept': 'application/json',
    },
)
with urllib.request.urlopen(request, timeout=60) as response:
    payload = json.load(response)

rows = []
for item in payload['stat_status_pairs']:
    stat = item['stat']
    rows.append({
        'frontendId': stat['frontend_question_id'],
        'questionId': stat['question_id'],
        'slug': stat['question__title_slug'],
        'title': stat['question__title'],
        'paidOnly': item['paid_only'],
        'level': item['difficulty']['level'],
        'acRate': stat.get('total_acs', 0) / stat['total_submitted'] if stat.get('total_submitted') else None,
    })

rows.sort(key=lambda r: r['frontendId'])
out_path = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
os.makedirs(out_path, exist_ok=True)
with open(os.path.join(out_path, 'all-problems.json'), 'w', encoding='utf-8') as handle:
    json.dump(rows, handle, ensure_ascii=False, indent=0)

free = [r for r in rows if not r['paidOnly']]
levels = {1: 'Easy', 2: 'Medium', 3: 'Hard'}
print(f'total problems: {len(rows)}')
print(f'free (non-premium): {len(free)}')
print(f'paid only: {len(rows) - len(free)}')
print()
from collections import Counter
print('free by difficulty:', dict(Counter(levels[r['level']] for r in free)))
print('max frontendId:', max(r['frontendId'] for r in rows))
