import urllib.request
import json
import os
import sys
from datetime import datetime, timezone

url = 'https://api.github.com/repos/arkadiyt/bounty-targets-data/commits/main'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
except Exception as e:
    print(f'Error fetching API: {e}')
    sys.exit(1)

commit_date_raw = data['commit']['committer']['date']
commit_msg = data['commit']['message'].split('\n')[0]
commit_url = data['html_url']

if commit_date_raw.endswith('Z'):
    commit_date_raw = commit_date_raw[:-1] + '+00:00'

commit_dt = datetime.fromisoformat(commit_date_raw)
now_dt = datetime.now(timezone.utc)
diff_seconds = int((now_dt - commit_dt).total_seconds())

print(f'Time difference in seconds: {diff_seconds}')

event_name = os.getenv('EVENT_NAME')
telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

if diff_seconds < 22500 or event_name == 'workflow_dispatch':
    text = f'🚨 تنبيه تحديث جديد في الـ Scope!\n\n📝 العملية: {commit_msg}\n🔗 التفاصيل: {commit_url}'
    
    send_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = json.dumps({'chat_id': telegram_chat_id, 'text': text}).encode('utf-8')
    
    send_req = urllib.request.Request(send_url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(send_req) as resp:
            print('Notification sent successfully to Telegram.')
    except Exception as e:
        print(f'Error sending Telegram message: {e}')
        sys.exit(1)
else:
    print('No new commits in the last 6 hours.')
