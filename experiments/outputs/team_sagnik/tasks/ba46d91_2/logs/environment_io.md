
### Environment Interaction 1
----------------------------------------------------------------------------
```python
supervisor_profile = apis.supervisor.show_profile()
supervisor_passwords = {p['account_name']: p['password'] for p in apis.supervisor.show_account_passwords()}
_ready_tokens = []
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'amazon' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        amazon_token = apis.amazon.login(username=_u, password=supervisor_passwords['amazon'])['access_token']
        _ready_tokens.append('amazon')
        break
    except Exception:
        continue
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'phone' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        phone_token = apis.phone.login(username=_u, password=supervisor_passwords['phone'])['access_token']
        _ready_tokens.append('phone')
        break
    except Exception:
        continue
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'file_system' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        file_system_token = apis.file_system.login(username=_u, password=supervisor_passwords['file_system'])['access_token']
        _ready_tokens.append('file_system')
        break
    except Exception:
        continue
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'spotify' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        spotify_token = apis.spotify.login(username=_u, password=supervisor_passwords['spotify'])['access_token']
        _ready_tokens.append('spotify')
        break
    except Exception:
        continue
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'venmo' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        venmo_token = apis.venmo.login(username=_u, password=supervisor_passwords['venmo'])['access_token']
        _ready_tokens.append('venmo')
        break
    except Exception:
        continue
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'gmail' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        gmail_token = apis.gmail.login(username=_u, password=supervisor_passwords['gmail'])['access_token']
        _ready_tokens.append('gmail')
        break
    except Exception:
        continue
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'splitwise' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        splitwise_token = apis.splitwise.login(username=_u, password=supervisor_passwords['splitwise'])['access_token']
        _ready_tokens.append('splitwise')
        break
    except Exception:
        continue
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'simple_note' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        simple_note_token = apis.simple_note.login(username=_u, password=supervisor_passwords['simple_note'])['access_token']
        _ready_tokens.append('simple_note')
        break
    except Exception:
        continue
for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] if 'todoist' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:
    try:
        todoist_token = apis.todoist.login(username=_u, password=supervisor_passwords['todoist'])['access_token']
        _ready_tokens.append('todoist')
        break
    except Exception:
        continue
print('BOOTSTRAP OK — ready tokens: ' + ', '.join(f'{a}_token' for a in _ready_tokens))
```

```
BOOTSTRAP OK — ready tokens: amazon_token, phone_token, file_system_token, spotify_token, venmo_token, gmail_token, splitwise_token, simple_note_token, todoist_token
```


### Environment Interaction 2
----------------------------------------------------------------------------
```python
prime_subscriptions = apis.amazon.show_prime_subscriptions(access_token=amazon_token)
print(prime_subscriptions)
current_date = apis.phone.get_current_date_and_time(access_token=phone_token)
print(current_date)
```

```
[
 {
  "prime_subscription_id": 122,
  "start_date": "2023-03-19T16:27:43",
  "end_date": "2024-03-18T23:59:59",
  "payment_card_digits": "4582",
  "paid_amount": 140.0
 },
 {
  "prime_subscription_id": 121,
  "start_date": "2023-02-16T16:27:43",
  "end_date": "2023-03-18T23:59:59",
  "payment_card_digits": "4582",
  "paid_amount": 15.0
 }
]
{"date": "Friday, May 19, 2023", "time": "12:00 AM"}
```


### Environment Interaction 3
----------------------------------------------------------------------------
```python
from datetime import datetime

prime_subscriptions = [
 {
  "prime_subscription_id": 122,
  "start_date": "2023-03-19T16:27:43",
  "end_date": "2024-03-18T23:59:59",
  "payment_card_digits": "4582",
  "paid_amount": 140.0
 },
 {
  "prime_subscription_id": 121,
  "start_date": "2023-02-16T16:27:43",
  "end_date": "2023-03-18T23:59:59",
  "payment_card_digits": "4582",
  "paid_amount": 15.0
 }
]
current_date = datetime.strptime("2023-05-19", "%Y-%m-%d")

active_subscription = None
for subscription in prime_subscriptions:
    end_date = datetime.strptime(subscription["end_date"][:10], "%Y-%m-%d")
    if end_date > current_date:
        active_subscription = subscription
        break

if active_subscription:
    end_date = datetime.strptime(active_subscription["end_date"][:10], "%Y-%m-%d")
    remaining_days = (end_date - current_date).days
    remaining_months = round(remaining_days / 30)
    print("Remaining months:", remaining_months)
    apis.supervisor.complete_task(answer=remaining_months)
else:
    print("No active subscription found.")
    apis.supervisor.complete_task(answer=0)
```

```
Remaining months: 10
```

