
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
drafts = apis.gmail.show_drafts(access_token=gmail_token)
print(drafts)
empty_drafts = [draft for draft in drafts if not draft['subject'] or not draft['body']]
print(empty_drafts)
for draft in empty_drafts:
    apis.gmail.delete_draft(draft_id=draft['draft_id'], access_token=gmail_token)
    print(f"Draft {draft['draft_id']} deleted")
apis.supervisor.complete_task()
```

```
[
 {
  "draft_id": 479,
  "subject": "Performance Review Schedules",
  "body": "Hello Adrian,\n\nYour performance review is scheduled for next week. Please prepare any materials or feedback you'd like to discuss.\n\nThanks,\nKatie",
  "belongs_to_email_thread_id": null,
  "response_to_email_id": null,
  "scheduled_send_at": null,
  "created_at": "2023-05-17T18:36:03",
  "updated_at": "2023-05-17T18:36:03",
  "recipients": [
   {
    "name": "Adrian Burton",
    "email": "adrian_burt@gmail.com"
   }
  ],
  "attachments": []
 },
 {
  "draft_id": 25,
  "subject": "Updated Office Security Protocols",
  "body": "Dear team,\n\nPlease review the updated security protocols for our office. It's important that everyone is aware and compliant. Safety first!\n\nCheers,\nKatie",
  "belongs_to_email_thread_id": null,
  "response_to_email_id": null,
  "scheduled_send_at": null,
  "created_at": "2023-05-15T13:30:25",
  "updated_at": "2023-05-15T13:30:25",
  "recipients": [
   {
    "name": "Bradley Ball",
    "email": "bradley_ball@gmail.com"
   },
   {
    "name": "Ronald Harrison",
    "email": "ron.harrison@gmail.com"
   },
   {
    "name": "Isaac Miller",
    "email": "ismill@gmail.com"
   },
   {
    "name": "Miranda Weber",
    "email": "mir-powe@gmail.com"
   },
   {
    "name": "Jeremy Calhoun",
    "email": "jer.calhoun@gmail.com"
   },
   {
    "name": "Mason Smith",
    "email": "masmith@gmail.com"
   },
   {
    "name": "Adrian Burton",
    "email": "adrian_burt@gmail.com"
   }
  ],
  "attachments": []
 },
 {
  "draft_id": 27,
  "subject": "Upcoming Project Deadlines",
  "body": "",
  "belongs_to_email_thread_id": null,
  "response_to_email_id": null,
  "scheduled_send_at": null,
  "created_at": "2023-05-11T08:36:31",
  "updated_at": "2023-05-11T08:36:31",
  "recipients": [
   {
    "name": "Bradley Ball",
    "email": "bradley_ball@gmail.com"
   },
   {
    "name": "Ronald Harrison",
    "email": "ron.harrison@gmail.com"
   },
   {
    "name": "Isaac Miller",
    "email": "ismill@gmail.com"
   },
   {
    "name": "Miranda Weber",
    "email": "mir-powe@gmail.com"
   },
   {
    "name": "Jeremy Calhoun",
    "email": "jer.calhoun@gmail.com"
   },
   {
    "name": "Mason Smith",
    "email": "masmith@gmail.com"
   },
   {
    "name": "Adrian Burton",
    "email": "adrian_burt@gmail.com"
   }
  ],
  "attachments": []
 },
 {
  "draft_id": 26,
  "subject": "Internship Program Applications Open",
  "body": "Hello team,\n\nOur internship program applications are now open! If you know any students or recent graduates who would be interested in joining our team, please share the attached flyer with them. We appreciate your help in spreading the word.\n\nBest regards,\nKatie\n",
  "belongs_to_email_thread_id": null,
  "response_to_email_id": null,
  "scheduled_send_at": null,
  "created_at": "2023-05-10T15:51:40",
  "updated_at": "2023-05-10T15:51:40",
  "recipients": [
   {
    "name": "Bradley Ball",
    "email": "bradley_ball@gmail.com"
   },
   {
    "name": "Ronald Harrison",
    "email": "ron.harrison@gmail.com"
   },
   {
    "name": "Isaac Miller",
    "email": "ismill@gmail.com"
   },
   {
    "name": "Miranda Weber",
    "email": "mir-powe@gmail.com"
   },
   {
    "name": "Jeremy Calhoun",
    "email": "jer.calhoun@gmail.com"
   },
   {
    "name": "Mason Smith",
    "email": "masmith@gmail.com"
   },
   {
    "name": "Adrian Burton",
    "email": "adrian_burt@gmail.com"
   }
  ],
  "attachments": []
 },
 {
  "draft_id": 85,
  "subject": "",
  "body": "",
  "belongs_to_email_thread_id": null,
  "response_to_email_id": null,
  "scheduled_send_at": null,
  "created_at": "2023-05-09T15:26:10",
  "updated_at": "2023-05-09T15:26:10",
  "recipients": [
   {
    "name": "Isaac Miller",
    "email": "ismill@gmail.com"
   },
   {
    "name": "Bradley Ball",
    "email": "bradley_ball@gmail.com"
   },
   {
    "name": "Ronald Harrison",
    "email": "ron.harrison@gmail.com"
   },
   {
    "name": "Miranda Weber",
    "email": "mir-powe@gmail.com"
   },
   {
    "name": "Jeremy Calhoun",
    "email": "jer.calhoun@gmail.com"
   },
   {
    "name": "Mason Smith",
    "email": "masmith@gmail.com"
   },
   {
    "name": "Adrian Burton",
    "email": "adrian_burt@gmail.com"
   }
  ],
  "attachments": []
 }
]
[
 {
  "draft_id": 27,
  "subject": "Upcoming Project Deadlines",
  "body": "",
  "belongs_to_email_thread_id": null,
  "response_to_email_id": null,
  "scheduled_send_at": null,
  "created_at": "2023-05-11T08:36:31",
  "updated_at": "2023-05-11T08:36:31",
  "recipients": [
   {
    "name": "Bradley Ball",
    "email": "bradley_ball@gmail.com"
   },
   {
    "name": "Ronald Harrison",
    "email": "ron.harrison@gmail.com"
   },
   {
    "name": "Isaac Miller",
    "email": "ismill@gmail.com"
   },
   {
    "name": "Miranda Weber",
    "email": "mir-powe@gmail.com"
   },
   {
    "name": "Jeremy Calhoun",
    "email": "jer.calhoun@gmail.com"
   },
   {
    "name": "Mason Smith",
    "email": "masmith@gmail.com"
   },
   {
    "name": "Adrian Burton",
    "email": "adrian_burt@gmail.com"
   }
  ],
  "attachments": []
 },
 {
  "draft_id": 85,
  "subject": "",
  "body": "",
  "belongs_to_email_thread_id": null,
  "response_to_email_id": null,
  "scheduled_send_at": null,
  "created_at": "2023-05-09T15:26:10",
  "updated_at": "2023-05-09T15:26:10",
  "recipients": [
   {
    "name": "Isaac Miller",
    "email": "ismill@gmail.com"
   },
   {
    "name": "Bradley Ball",
    "email": "bradley_ball@gmail.com"
   },
   {
    "name": "Ronald Harrison",
    "email": "ron.harrison@gmail.com"
   },
   {
    "name": "Miranda Weber",
    "email": "mir-powe@gmail.com"
   },
   {
    "name": "Jeremy Calhoun",
    "email": "jer.calhoun@gmail.com"
   },
   {
    "name": "Mason Smith",
    "email": "masmith@gmail.com"
   },
   {
    "name": "Adrian Burton",
    "email": "adrian_burt@gmail.com"
   }
  ],
  "attachments": []
 }
]
Draft 27 deleted
Draft 85 deleted
```

