
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
wish_list = apis.amazon.show_wish_list(access_token=amazon_token)
print(wish_list)
partner = apis.phone.search_contacts(relationship='partner', access_token=phone_token)[0]
print(partner)
message = "\n".join(f"{product['product_name']} => ${round(product['price'] * product['quantity'])}" for product in wish_list)
print(message)
apis.phone.send_text_message(phone_number=partner['phone_number'], message=message, access_token=phone_token)
apis.supervisor.complete_task()
```

```
[
 {
  "product_id": 55,
  "product_name": "3M Scotch 8-in Cable Ties",
  "quantity": 2,
  "price": 2.5
 },
 {
  "product_id": 387,
  "product_name": "Sawyer Products Mini Water Filtration System",
  "quantity": 1,
  "price": 24.9
 },
 {
  "product_id": 597,
  "product_name": "Hamilton Beach 8-Cup Compact Food Processor",
  "quantity": 1,
  "price": 30.0
 },
 {
  "product_id": 1651,
  "product_name": "Craftsman 8-Inch Arc Joint Pliers",
  "quantity": 1,
  "price": 9.0
 },
 {
  "product_id": 1688,
  "product_name": "Husky Adjustable Height Work Table",
  "quantity": 1,
  "price": 199.0
 },
 {
  "product_id": 2100,
  "product_name": "Ascend Trekking Poles",
  "quantity": 1,
  "price": 30.0
 },
 {
  "product_id": 2218,
  "product_name": "OXO Good Grips\u00ae Stainless Steel Soap Dispenser",
  "quantity": 1,
  "price": 20.0
 }
]
{
 "contact_id": 1007,
 "first_name": "Marcus",
 "last_name": "Smith",
 "email": "ma_smith@gmail.com",
 "phone_number": "7196131136",
 "relationships": [
  "partner",
  "husband"
 ],
 "birthday": "1986-02-21",
 "home_address": "3516 Kevin Village Suite 778\nSeattle\nWashington\nUnited States\n86248",
 "work_address": "96967 Fox Loop Suite 397\nSeattle\nWashington\nUnited States\n86832",
 "created_at": "2021-04-10T18:11:42"
}
3M Scotch 8-in Cable Ties => $5
Sawyer Products Mini Water Filtration System => $25
Hamilton Beach 8-Cup Compact Food Processor => $30
Craftsman 8-Inch Arc Joint Pliers => $9
Husky Adjustable Height Work Table => $199
Ascend Trekking Poles => $30
OXO Good Grips® Stainless Steel Soap Dispenser => $20
```

