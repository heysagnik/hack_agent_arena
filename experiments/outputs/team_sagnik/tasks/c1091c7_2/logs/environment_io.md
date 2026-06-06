
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
inbox_threads = apis.gmail.show_inbox_threads(query="meeting canceled", access_token=gmail_token)
print(inbox_threads)
```

```
[
 {
  "email_thread_id": 47823,
  "email_ids": [
   20868
  ],
  "draft_ids": [],
  "incoming": true,
  "outgoing": false,
  "read": false,
  "label": null,
  "starred": false,
  "archived": false,
  "spam": false,
  "created_at": "2023-05-21T18:23:44",
  "updated_at": "2023-05-21T18:23:44",
  "subject": "Cancel Meeting?",
  "participants": [
   {
    "name": "Cesar Maldonado",
    "email": "ce-maldonado@gmail.com"
   },
   {
    "name": "Catherine Smith",
    "email": "ca-smit@gmail.com"
   }
  ]
 },
 {
  "email_thread_id": 47833,
  "email_ids": [
   20875,
   20876
  ],
  "draft_ids": [],
  "incoming": true,
  "outgoing": true,
  "read": false,
  "label": null,
  "starred": false,
  "archived": false,
  "spam": false,
  "created_at": "2023-05-22T09:29:14",
  "updated_at": "2023-05-22T09:29:14",
  "subject": "Reunion Cancelation",
  "participants": [
   {
    "name": "Alex White",
    "email": "alexwhite@gmail.com"
   },
   {
    "name": "Cesar Maldonado",
    "email": "ce-maldonado@gmail.com"
   }
  ]
 },
 {
  "email_thread_id": 47829,
  "email_ids": [
   20871,
   20872
  ],
  "draft_ids": [],
  "incoming": true,
  "outgoing": true,
  "read": false,
  "label": null,
  "starred": false,
  "archived": false,
  "spam": false,
  "created_at": "2023-05-22T10:39:27",
  "updated_at": "2023-05-22T10:39:27",
  "subject": "Good Update for Meeting",
  "participants": [
   {
    "name": "Christopher Burch",
    "email": "ch-burch@gmail.com"
   },
   {
    "name": "Cesar Maldonado",
    "email": "ce-maldonado@gmail.com"
   }
  ]
 },
 {
  "email_thread_id": 47831,
  "email_ids": [
   20873,
   20874
  ],
  "draft_ids": [],
  "incoming": true,
  "outgoing": true,
  "read": false,
  "label": null,
  "starred": false,
  "archived": false,
  "spam": false,
  "created_at": "2023-05-22T09:37:36",
  "updated_at": "2023-05-22T09:37:36",
  "subject": "Meeting Minutes",
  "participants": [
   {
    "name": "Tracy Weber",
    "email": "tra_weber@gmail.com"
   },
   {
    "name": "Cesar Maldonado",
    "email": "ce-maldonado@gmail.com"
   }
  ]
 },
 {
  "email_thread_id": 13900,
  "email_ids": [
   4329
  ],
  "draft_ids": [],
  "incoming": true,
  "outgoing": false,
  "read": false,
  "label": null,
  "starred": false,
  "archived": false,
  "spam": false,
  "created_at": "2023-04-25T10:18:08",
  "updated_at": "2023-04-25T10:18:08",
  "subject": "Request for Overtime Approval",
  "participants": [
   {
    "name": "Cesar Maldonado",
    "email": "ce-maldonado@gmail.com"
   },
   {
    "name": "Brian Ritter",
    "email": "br_ritt@gmail.com"
   }
  ]
 }
]
```


### Environment Interaction 3
----------------------------------------------------------------------------
```python
canceled_threads = [thread for thread in inbox_threads if "cancel" in thread["subject"].lower()]
email_ids = [email_id for thread in canceled_threads for email_id in thread["email_ids"]]
print(email_ids)

for email_id in email_ids:
    email = apis.gmail.show_email(email_id=email_id, access_token=gmail_token)
    print(email)
```

```
[20868, 20875, 20876]
{
 "email_id": 20868,
 "subject": "Cancel Meeting?",
 "body": "I am swamped with a deadline. Cannot make it. Apologies.\nBest, Catherine Smith",
 "response_to_email_id": null,
 "created_at": "2023-05-21T18:23:44",
 "sender": {
  "name": "Catherine Smith",
  "email": "ca-smit@gmail.com"
 },
 "recipients": [
  {
   "name": "Cesar Maldonado",
   "email": "ce-maldonado@gmail.com"
  }
 ],
 "attachments": []
}
{
 "email_id": 20875,
 "subject": "Reunion Cancelation",
 "body": "Unfortunately everone is busy this weekend. Let's cancel the reunion.\nBest,\nAlex White",
 "response_to_email_id": null,
 "created_at": "2023-05-22T09:29:14",
 "sender": {
  "name": "Alex White",
  "email": "alexwhite@gmail.com"
 },
 "recipients": [
  {
   "name": "Cesar Maldonado",
   "email": "ce-maldonado@gmail.com"
  }
 ],
 "attachments": []
}
{
 "email_id": 20876,
 "subject": "Re: Reunion Cancelation",
 "body": "Okay, no problem.",
 "response_to_email_id": 20875,
 "created_at": "2023-05-22T09:33:45",
 "sender": {
  "name": "Cesar Maldonado",
  "email": "ce-maldonado@gmail.com"
 },
 "recipients": [
  {
   "name": "Alex White",
   "email": "alexwhite@gmail.com"
  }
 ],
 "attachments": []
}
```


### Environment Interaction 4
----------------------------------------------------------------------------
```python
alarms = apis.phone.show_alarms(access_token=phone_token)
print(alarms)

for alarm in alarms:
    for email in [20868, 20875, 20876]:
        email_content = apis.gmail.show_email(email_id=email, access_token=gmail_token)
        if email_content["sender"]["name"] in alarm["label"]:
            apis.phone.update_alarm(alarm_id=alarm["alarm_id"], enabled=False, access_token=phone_token)
            print(f"Alarm {alarm['alarm_id']} disabled")
```

```
[
 {
  "alarm_id": 603,
  "time": "08:30",
  "repeat_days": [
   "monday",
   "tuesday",
   "wednesday",
   "thursday",
   "friday"
  ],
  "label": "Wake Up",
  "enabled": true,
  "snooze_minutes": 10,
  "vibration": true,
  "created_at": "2023-05-18T12:00:00",
  "user": {
   "name": "Cesar Maldonado",
   "phone_number": "3947324235"
  }
 },
 {
  "alarm_id": 747,
  "time": "09:00",
  "repeat_days": [
   "tuesday"
  ],
  "label": "One-on-One with Christopher",
  "enabled": true,
  "snooze_minutes": 15,
  "vibration": true,
  "created_at": "2023-05-08T09:32:45",
  "user": {
   "name": "Cesar Maldonado",
   "phone_number": "3947324235"
  }
 },
 {
  "alarm_id": 604,
  "time": "09:30",
  "repeat_days": [
   "saturday",
   "sunday"
  ],
  "label": "Wake Up",
  "enabled": true,
  "snooze_minutes": 10,
  "vibration": true,
  "created_at": "2023-05-18T12:00:00",
  "user": {
   "name": "Cesar Maldonado",
   "phone_number": "3947324235"
  }
 },
 {
  "alarm_id": 749,
  "time": "09:30",
  "repeat_days": [
   "tuesday"
  ],
  "label": "One-on-One with Thomas",
  "enabled": true,
  "snooze_minutes": 15,
  "vibration": true,
  "created_at": "2023-05-09T08:20:32",
  "user": {
   "name": "Cesar Maldonado",
   "phone_number": "3947324235"
  }
 },
 {
  "alarm_id": 606,
  "time": "10:30",
  "repeat_days": [
   "monday"
  ],
  "label": "Weekly Work Standup Meeting",
  "enabled": true,
  "snooze_minutes": 0,
  "vibration": true,
  "created_at": "2023-05-18T12:00:00",
  "user": {
   "name": "Cesar Maldonado",
   "phone_number": "3947324235"
  }
 }
]
```


### Environment Interaction 5
----------------------------------------------------------------------------
```python
senders = ["Catherine Smith", "Alex White"]
for sender in senders:
    contacts = apis.phone.search_contacts(query=sender, access_token=phone_token)
    print(contacts)
    if contacts:
        for alarm in alarms:
            if sender in alarm["label"]:
                apis.phone.update_alarm(alarm_id=alarm["alarm_id"], enabled=False, access_token=phone_token)
                print(f"Alarm {alarm['alarm_id']} disabled")
apis.supervisor.complete_task()
```

```
[
 {
  "contact_id": 1776,
  "first_name": "Catherine",
  "last_name": "Smith",
  "email": "ca-smit@gmail.com",
  "phone_number": "9084969795",
  "relationships": [
   "subordinate",
   "coworker"
  ],
  "birthday": "1951-11-27",
  "home_address": "40859 French Spring Suite 468\nSeattle\nWashington\nUnited States\n12477",
  "work_address": "5840 Craig Turnpike Suite 634\nSeattle\nWashington\nUnited States\n78487",
  "created_at": "2022-11-23T16:33:45"
 },
 {
  "contact_id": 1789,
  "first_name": "Cody",
  "last_name": "Smith",
  "email": "cod.smith@gmail.com",
  "phone_number": "7826309761",
  "relationships": [
   "friend"
  ],
  "birthday": "1993-03-02",
  "home_address": "8948 Owens Via Suite 628\nSeattle\nWashington\nUnited States\n75367",
  "work_address": "7844 Joshua Shore Suite 460\nSeattle\nWashington\nUnited States\n46946",
  "created_at": "2022-11-23T16:33:45"
 },
 {
  "contact_id": 1769,
  "first_name": "Katherine",
  "last_name": "Smith",
  "email": "ka_ball@gmail.com",
  "phone_number": "7863159797",
  "relationships": [
   "subordinate",
   "coworker"
  ],
  "birthday": "1985-11-16",
  "home_address": "8948 Owens Via Suite 628\nSeattle\nWashington\nUnited States\n75367",
  "work_address": "5840 Craig Turnpike Suite 634\nSeattle\nWashington\nUnited States\n78487",
  "created_at": "2022-11-23T16:33:45"
 },
 {
  "contact_id": 1770,
  "first_name": "Thomas",
  "last_name": "Solomon",
  "email": "thomas.solomon@gmail.com",
  "phone_number": "2192158297",
  "relationships": [
   "subordinate",
   "coworker"
  ],
  "birthday": "1958-02-21",
  "home_address": "2317 Powell Stream Suite 570\nSeattle\nWashington\nUnited States\n32418",
  "work_address": "5840 Craig Turnpike Suite 634\nSeattle\nWashington\nUnited States\n78487",
  "created_at": "2022-11-23T16:33:45"
 },
 {
  "contact_id": 1771,
  "first_name": "Jessica",
  "last_name": "Miller",
  "email": "jes.mill@gmail.com",
  "phone_number": "3808719492",
  "relationships": [
   "subordinate",
   "coworker"
  ],
  "birthday": "1962-11-19",
  "home_address": "82352 Russell Views Suite 600\nSeattle\nWashington\nUnited States\n36974",
  "work_address": "5840 Craig Turnpike Suite 634\nSeattle\nWashington\nUnited States\n78487",
  "created_at": "2022-11-23T16:33:45"
 }
]
[
 {
  "contact_id": 1790,
  "first_name": "Alex",
  "last_name": "White",
  "email": "alexwhite@gmail.com",
  "phone_number": "3707865891",
  "relationships": [
   "friend"
  ],
  "birthday": "1981-10-14",
  "home_address": "0031 Jeremy Cliff Suite 552\nSeattle\nWashington\nUnited States\n72731",
  "work_address": "406 Lindsay Courts Suite 522\nSeattle\nWashington\nUnited States\n26281",
  "created_at": "2022-11-23T16:33:45"
 },
 {
  "contact_id": 1785,
  "first_name": "Kristin",
  "last_name": "White",
  "email": "kri-powe@gmail.com",
  "phone_number": "6017026518",
  "relationships": [
   "friend"
  ],
  "birthday": "1987-05-31",
  "home_address": "0031 Jeremy Cliff Suite 552\nSeattle\nWashington\nUnited States\n72731",
  "work_address": "7844 Joshua Shore Suite 460\nSeattle\nWashington\nUnited States\n46946",
  "created_at": "2022-11-23T16:33:45"
 },
 {
  "contact_id": 1769,
  "first_name": "Katherine",
  "last_name": "Smith",
  "email": "ka_ball@gmail.com",
  "phone_number": "7863159797",
  "relationships": [
   "subordinate",
   "coworker"
  ],
  "birthday": "1985-11-16",
  "home_address": "8948 Owens Via Suite 628\nSeattle\nWashington\nUnited States\n75367",
  "work_address": "5840 Craig Turnpike Suite 634\nSeattle\nWashington\nUnited States\n78487",
  "created_at": "2022-11-23T16:33:45"
 },
 {
  "contact_id": 1770,
  "first_name": "Thomas",
  "last_name": "Solomon",
  "email": "thomas.solomon@gmail.com",
  "phone_number": "2192158297",
  "relationships": [
   "subordinate",
   "coworker"
  ],
  "birthday": "1958-02-21",
  "home_address": "2317 Powell Stream Suite 570\nSeattle\nWashington\nUnited States\n32418",
  "work_address": "5840 Craig Turnpike Suite 634\nSeattle\nWashington\nUnited States\n78487",
  "created_at": "2022-11-23T16:33:45"
 },
 {
  "contact_id": 1771,
  "first_name": "Jessica",
  "last_name": "Miller",
  "email": "jes.mill@gmail.com",
  "phone_number": "3808719492",
  "relationships": [
   "subordinate",
   "coworker"
  ],
  "birthday": "1962-11-19",
  "home_address": "82352 Russell Views Suite 600\nSeattle\nWashington\nUnited States\n36974",
  "work_address": "5840 Craig Turnpike Suite 634\nSeattle\nWashington\nUnited States\n78487",
  "created_at": "2022-11-23T16:33:45"
 }
]
```

