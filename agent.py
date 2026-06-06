"""
hack_agent_arena — AppWorld agent.

Stack:
  - LLM:    OpenRouter API (meta-llama/llama-3.3-70b-instruct) via OpenAI-compatible client
  - Memory: HydraDB two-lane — knowledge (API docs) + memory (past wins)
  - Loop:   ReAct with N+1 blocking, error recovery, step budgeting

Run:
  export OPENROUTER_API_KEY=sk-or-...
  export HYDRA_DB_API_KEY=...
  export APPWORLD_EXPERIMENT=team_<name>
  export APPWORLD_DATASET=dev
  python agent.py
"""

import builtins
import json
import os
import re
import signal
import time

# Windows stub — AppWorld uses SIGALRM internally, which doesn't exist on Windows
if not hasattr(signal, "SIGALRM"):
    signal.SIGALRM = None  # type: ignore[attr-defined]
    signal.alarm = lambda seconds: None  # type: ignore[attr-defined]
    _orig_signal = signal.signal

    def _signal_compat(sig, handler):
        if sig is not None:
            return _orig_signal(sig, handler)

    signal.signal = _signal_compat  # type: ignore[assignment]

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from appworld import AppWorld, load_task_ids
from openai import OpenAI

# ── config ────────────────────────────────────────────────────────────────────
MODEL            = os.environ.get("MODEL", "meta-llama/llama-3.3-70b-instruct")
DATASET          = os.environ.get("APPWORLD_DATASET", "dev")
EXPERIMENT       = os.environ.get("APPWORLD_EXPERIMENT", "team_demo")
MAX_INTERACTIONS = int(os.environ.get("MAX_INTERACTIONS", "100"))
MAX_FAIL_STREAK  = int(os.environ.get("MAX_FAIL_STREAK", "12"))  # abort task after this many error turns w/o progress
MAX_CODE_REPEATS = int(os.environ.get("MAX_CODE_REPEATS", "3"))  # abort task if same code submitted this many times
MAX_TASKS        = int(os.environ.get("MAX_TASKS", "0"))
SKIP_TASKS       = int(os.environ.get("SKIP_TASKS", "0"))
MAX_OUTPUT_CHARS = int(os.environ.get("MAX_OUTPUT_CHARS", "4000"))
TRAJECTORY_CHARS = int(os.environ.get("TRAJECTORY_CHARS", "20000"))
MAX_TOKENS       = int(os.environ.get("MAX_TOKENS", "2048"))
STEP_DELAY       = float(os.environ.get("STEP_DELAY", "0.5"))
TASK_DELAY       = float(os.environ.get("TASK_DELAY", "5"))
API_DOCS_DIR     = os.environ.get("API_DOCS_DIR", "data/api_docs/function_calling")

HYDRA_KEY         = os.environ.get("HYDRA_DB_API_KEY", "")
HYDRA_TENANT      = os.environ.get("HYDRA_TENANT", "appworld-v1")
HYDRA_MEM_TENANT  = os.environ.get("HYDRA_MEM_TENANT", "appworld-task-memory")
HYDRA_API_RESULTS = int(os.environ.get("HYDRA_API_RESULTS", "3"))
HYDRA_MEM_RESULTS = int(os.environ.get("HYDRA_MEM_RESULTS", "2"))

_INTERNAL_APPS   = {"supervisor", "api_docs", "admin"}
_LLM_RETRY_WAITS = [5, 15, 30, 60, 90]  # OpenRouter 429 backoff

_QUESTION_RE = re.compile(
    r"\b(how many|how much|what is|what are|what was|what were|who is|who are|"
    r"what'?s|which|when is|when are|where is|find the|tell me|show me|"
    r"count|total|number of|amount of|name of|list all|list the)\b",
    re.I,
)

llm_client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://github.com/hack-agent-arena",
        "X-Title": "hack-agent-arena",
    },
)

# ── HydraDB ───────────────────────────────────────────────────────────────────
_hydra_client = None
_build_string  = None


def _hydra():
    global _hydra_client, _build_string
    if _hydra_client is None and HYDRA_KEY:
        from hydra_db import HydraDB
        from hydra_db.helpers import build_string
        _hydra_client = HydraDB(token=HYDRA_KEY)
        _build_string = build_string
    return _hydra_client


def _hydra_query(tenant_id: str, query_type: str, query: str, n: int) -> str:
    client = _hydra()
    if not client or not n:
        return ""
    try:
        results = client.query(
            tenant_id=tenant_id, query=query, type=query_type,
            query_by="hybrid", mode="fast", max_results=n,
        )
        return _build_string(results).strip()
    except Exception as e:
        print(f"  [hydra/{query_type}] query failed: {e}")
        return ""


def _clean_api_doc_chunks(raw: str) -> str:
    """Strip HydraDB's JSON envelope, keeping only the readable 'APP: ... | API: ...'
    doc text for each retrieved chunk — leaner and clearer for the model."""
    texts = re.findall(r'"text":\s*"((?:[^"\\]|\\.)*)"', raw)
    if not texts:
        return raw.strip()
    cleaned = []
    for t in texts:
        for _ in range(2):  # docs were JSON-in-JSON ingested → may be doubly escaped
            if "\\n" not in t and '\\"' not in t:
                break
            t = (t.replace("\\\\", "\x00").replace('\\"', '"').replace("\\n", "\n")
                  .replace("\\t", "\t").replace("\x00", "\\"))
        cleaned.append(t.strip())
    return "\n\n---\n\n".join(cleaned)


def retrieve_api_docs(instruction: str) -> str:
    text = _clean_api_doc_chunks(
        _hydra_query(HYDRA_TENANT, "knowledge", instruction, HYDRA_API_RESULTS)
    )
    if text:
        print(f"  [hydra/knowledge] {HYDRA_API_RESULTS} API docs retrieved ({len(text)} chars)")
    return text


def retrieve_task_memories(instruction: str) -> str:
    text = _hydra_query(HYDRA_MEM_TENANT, "memory", instruction, HYDRA_MEM_RESULTS)
    if text:
        print(f"  [hydra/memory] {HYDRA_MEM_RESULTS} memories retrieved")
    return text


def store_task_memory(task_id: str, instruction: str, apis_used: list[str], steps: int) -> None:
    client = _hydra()
    if not client:
        return
    try:
        client.context.ingest(
            type="memory",
            tenant_id=HYDRA_MEM_TENANT,
            memories=json.dumps([{
                "id": f"task-{task_id}",
                "title": instruction[:80],
                "text": (
                    f"Task: {instruction}\n"
                    f"APIs used: {', '.join(apis_used)}\n"
                    f"Completed in {steps} steps."
                ),
                "infer": False,
            }]),
        )
        print(f"  [hydra/memory] stored pattern for task {task_id}")
    except Exception as e:
        print(f"  [hydra/memory] store failed: {e}")


def extract_apis_used(messages: list[dict]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for msg in messages:
        if msg.get("role") != "assistant":
            continue
        for m in re.finditer(r"apis\.(\w+)\.(\w+)\(", msg.get("content", "")):
            key = f"{m.group(1)}.{m.group(2)}"
            if key not in seen:
                seen.add(key)
                ordered.append(key)
    return ordered


# ── ground-truth API surface (so the model picks real APIs, never hallucinates) ─
_api_names_cache: dict[str, list[str]] = {}


def _app_api_names(app: str) -> list[str]:
    """Real API names for an app, read from the AppWorld api_docs (app prefix stripped)."""
    if app in _api_names_cache:
        return _api_names_cache[app]
    names: list[str] = []
    try:
        with open(os.path.join(API_DOCS_DIR, f"{app}.json"), encoding="utf-8") as f:
            for item in json.load(f):
                fn = item.get("function", item)
                name = fn.get("name", "")
                name = name.split("__", 1)[1] if "__" in name else name
                if name and name not in ("login", "logout", "signup"):
                    names.append(name)
    except Exception:
        names = []
    _api_names_cache[app] = names
    return names


def build_api_menu(allowed_apps: list[str]) -> str:
    """Per-task menu of the ONLY real APIs available, grouped by app — data-derived,
    so the model selects an existing API instead of guessing one that doesn't exist."""
    lines = []
    for app in [a for a in allowed_apps if a not in _INTERNAL_APPS]:
        names = _app_api_names(app)
        if names:
            lines.append(f"  {app}: {', '.join(names)}")
    return "\n".join(lines)


# ── system prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an AI agent completing tasks by writing Python code against app APIs.

EACH TURN, OUTPUT EXACTLY TWO PARTS:
  1. `Thought:` ONE line — what you learned from the last output and what this block will do.
  2. ONE ```python\\n...\\n``` block. The environment runs it statefully (variables persist) and shows output.
Repeat the Thought → Code → Observation loop until the task is done.

SETUP DONE: supervisor_profile, supervisor_passwords, and <app>_token vars already exist. Use them directly.
Never call show_profile / show_account_passwords / login — those are pre-done and waste your turns.

GOAL: Complete the task in as FEW turns as possible. Each turn should do REAL work — fetch AND process AND act in ONE block. Never use a turn just to inspect; always continue to the next step in the same block.

PRINT RULE: ALWAYS print() every API result. "Execution successful." means you forgot to print — that turn is wasted. Every variable you fetch must be printed if you need to use it next turn.

MULTI-STEP IN ONE BLOCK — do this:
```python
contacts = apis.phone.search_contacts(query="Alice", access_token=phone_token)
print(contacts)
email = contacts[0]["email"]
apis.gmail.send_email(email_addresses=[email], subject="Hi", body="Hello", access_token=gmail_token)
apis.supervisor.complete_task()
```

COMPLETION:
  Question (how many/what is/who/which): apis.supervisor.complete_task(answer="value")
  Action (send/add/delete/create):       apis.supervisor.complete_task()

API LOOKUP — consult docs BEFORE guessing an API or param you are not sure of (do not hallucinate names):
  print(apis.api_docs.show_api_descriptions(app_name='venmo'))           # list an app's APIs
  print(apis.api_docs.show_api_doc(app_name='venmo', api_name='create_transaction'))  # exact params
If an API is NOT in the KNOWN APIS list below, look it up before calling it.

KNOWN APIS (verified real names — call directly; for any OTHER api use show_api_descriptions first):
  spotify:     search_songs, search_albums, search_playlists, show_song, show_playlist, show_playlist_library, create_playlist, add_song_to_playlist, remove_song_from_playlist, like_song, show_liked_songs, play_music, pause_music
  gmail:       show_inbox_threads, show_outbox_threads, show_thread, show_email, send_email, reply_to_email, show_drafts, show_draft, create_draft, update_draft, delete_draft, delete_email_in_thread, delete_thread
               ↳ gmail has NO search_emails / get_inbox. To search emails use show_inbox_threads(query=..., access_token=...).
               ↳ keys: threads use email_thread_id, emails use email_id, drafts use draft_id (never plain 'id'/'thread_id').
               ↳ flow: show_inbox_threads(query=) → t['email_thread_id'] → show_thread(email_thread_id=) → e['email_id'] → show_email(email_id=).
  venmo:       show_transactions, show_transaction, create_transaction, create_payment_request, show_received_payment_requests, show_sent_payment_requests, approve_payment_request, show_venmo_balance
  amazon:      search_products, show_product, show_orders, show_order, place_order, add_product_to_cart, show_cart, show_prime_subscriptions, show_prime_plans, subscribe_prime
  splitwise:   show_groups, show_group, record_expense, show_group_expenses, show_no_group_expenses, show_expense, show_group_balance, show_person_balance, settle_up, record_payment
  phone:       search_contacts, add_contact, update_contact, delete_contact, search_text_messages, send_text_message, show_text_message_window, get_current_date_and_time
               ↳ phone login uses username=supervisor_profile['phone_number'] (NOT email).
               ↳ search_contacts returns a LIST of contact dicts → use contacts[0]['phone_number'].
  simple_note: search_notes, show_note, create_note, update_note, add_content_to_note, delete_note
  todoist:     show_projects, show_tasks, create_task, show_task, update_task, delete_task   (NO complete_task — mark done via update_task)
  file_system: show_directory, show_file, create_file, update_file, delete_file, create_directory, move_file, copy_file

EXACT PARAMS for common actions (these are NOT 'to'/'message' — a wrong name gives a misleading error, not a clear one):
  gmail.send_email(email_addresses=[list], subject, body, access_token)     # email_addresses is a LIST, not 'to'
  gmail.reply_to_email(email_id, body, access_token)
  phone.send_text_message(phone_number, message, access_token)              # 'phone_number' + 'message', NOT 'to'/'body'
  venmo.create_transaction(receiver_email, amount, description, access_token)
  amazon.place_order(payment_card_id, address_id, access_token)             # orders the CART; no product arg here
  splitwise.record_expense(description, paid_amount, payer_email, debtor_emails=[list], debt_amounts=[list], group_id, access_token)

WORKFLOWS (verified — use these patterns for multi-step tasks):
  • Find people by relation: apis.phone.search_contacts(relationship='roommate'/'partner'/'husband'/'wife', access_token=phone_token).
    Each contact has 'name','phone_number','email'. (relationship= is far more reliable than query='partner'.)
  • Buy on amazon: search_products(query=, min_price=, max_price=, min_product_rating=, sort_by='product_rating', seller_id=, access_token=)
    → pick product → add_product_to_cart(product_id=, quantity=, access_token=) → choose home from show_addresses()
    → choose card from show_payment_cards() → place_order(payment_card_id=, address_id=, access_token=). Order one cart per recipient/address.
  • Disable phone alarms: show_alarms() → update_alarm(alarm_id=, enabled=False, access_token=).
  • Splitwise: find group via show_groups() → record_expense(group_id=, ...). Equal split → debt_amounts each = paid_amount/num_people.
  • 'home'/'my address' = the address in show_addresses() flagged default or matching supervisor; print and pick deliberately.

RULES:
1. ALWAYS print() every API call result — no silent fetches.
2. Do as much as possible per block — fetch, filter, act, complete in one shot.
3. Never guess field names — print the response first if unsure.
4. On error: fix only the failing line. Never repeat identical code.
5. PAGINATE list APIs: loop page_index=0,1,2,... (page_limit up to 20) and stop when a page returns []. Page 0 alone misses items.
6. To find specific items, prefer a filtered search (search_products(min_price=...), show_inbox_threads(query=...),
   search_contacts(relationship=...)) over fetching everything; only loop show_X() when you already have the specific ids.
7. Dates: use apis.phone.get_current_date_and_time() or pendulum — the env date is 2023-ish, NOT real today.
   "this week/month/year" is relative to the env date; compute the range explicitly before filtering.
8. Answer = plain string/number — no JSON, no sentences.
9. Always pass access_token= to every API call.
9b. ALWAYS use keyword arguments — apis.app.method(param=value, access_token=tok). Positional args fail with
    "_api_request() takes 0 positional arguments".
10. NEVER invent field names, IDs, or values — read them from a printed response. If unsure, print first.
11. ID keys are named <entity>_id (draft_id, order_id, product_id, group_id) — NEVER plain 'id' or 'messageId'.
    On KeyError, print(list(obj.keys())) and use a key that actually appears there.
12. NEVER assume a task detail not stated — if the instruction is ambiguous, inspect the data to resolve it, don't guess.
13. On failure, diagnose from the error/traceback and change approach — don't repeat the same call."""


# ── prompt builder ────────────────────────────────────────────────────────────
def classify_task(instruction: str) -> str:
    return "question" if _QUESTION_RE.search(instruction) else "action"


def build_task_prompt(instruction: str, sup: dict, allowed_apps: list[str],
                      api_docs: str, memories: str,
                      ready_tokens: list[str] | None = None) -> str:
    task_type = classify_task(instruction)
    completion_hint = (
        'QUESTION — call complete_task(answer="...") with your answer.'
        if task_type == "question"
        else "ACTION — call complete_task() with no argument when done."
    )
    relevant_apps = [a for a in allowed_apps if a not in _INTERNAL_APPS]

    lines = [
        "━━━ TASK CONTEXT ━━━",
        f"Supervisor: {sup['first_name']} {sup['last_name']} "
        f"(email: {sup.get('email', 'N/A')}, phone: {sup.get('phone_number', 'N/A')})",
    ]
    if relevant_apps:
        lines.append(f"Apps for this task: {', '.join(relevant_apps)}")

    ready_tokens = ready_tokens or []
    if ready_tokens:
        token_vars = ", ".join(f"{a}_token" for a in ready_tokens)
        lines.append(
            f"Ready tokens (already created — use directly, do NOT log in again): {token_vars}"
        )
        missing = [a for a in relevant_apps if a not in ready_tokens]
        if missing:
            first = missing[0]
            uname = ("supervisor_profile['phone_number']" if first == "phone"
                     else "supervisor_profile['email']")
            lines.append(
                f"NOT pre-logged-in: {', '.join(missing)}. To use one, log in FIRST with this exact pattern "
                f"(note ['access_token']; phone uses phone_number, all others use email):\n"
                f"    {first}_token = apis.{first}.login("
                f"username={uname}, password=supervisor_passwords['{first}'])['access_token']"
            )
    else:
        lines.append(
            "Setup NOT pre-run — start with the mandatory profile + passwords + login step."
        )

    lines += [
        f"Task type: {completion_hint}",
        f"\nTask: {instruction}",
    ]

    api_menu = build_api_menu(allowed_apps)
    if api_menu:
        lines += [
            "\n━━━ AVAILABLE APIS (the ONLY real APIs for this task — pick from these, never invent names) ━━━",
            api_menu,
            "Before calling an API whose parameters you are not certain of, FIRST understand it with:",
            "    print(apis.api_docs.show_api_doc(app_name='<app>', api_name='<api>'))",
            "then call it with the exact keyword params it lists. Confirm names from a printed response — never assume.",
        ]
    if memories:
        lines += ["\n━━━ SIMILAR PAST TASKS (guidance only) ━━━", memories]
    if api_docs:
        lines += ["\n━━━ RELEVANT API DOCS ━━━", api_docs]
    setup_note = (
        f"Budget: {MAX_INTERACTIONS} turns. Tokens are ready — start on the task immediately."
        if ready_tokens else
        f"Budget: {MAX_INTERACTIONS} turns. Begin: show_profile → show_account_passwords → login."
    )
    lines.append(f"\n{setup_note}")
    return "\n".join(lines)


# ── LLM ──────────────────────────────────────────────────────────────────────
_KEEP_FULL_OBS = 2  # paper: keep observations from the last 2 steps in full
_COLLAPSED     = "[NOT SHOWN FOR BREVITY]"


def _prune_messages(messages: list[dict]) -> list[dict]:
    """Paper-style context management (AppWorld §scaffold): keep every Thought/Code
    and the task context (messages[0]) intact; collapse observations older than the
    last _KEEP_FULL_OBS steps to a placeholder; if still over TRAJECTORY_CHARS, drop
    the oldest turns first."""
    obs_idx   = [i for i, m in enumerate(messages) if i > 0 and m["role"] == "user"]
    keep_full = set(obs_idx[-_KEEP_FULL_OBS:])

    out = []
    for i, m in enumerate(messages):
        if i == 0 or i in keep_full or m["role"] != "user":
            out.append(m)
        else:
            out.append({"role": "user", "content": _COLLAPSED})

    total = lambda msgs: sum(len(x["content"]) for x in msgs)
    while total(out) > TRAJECTORY_CHARS and len(out) > 1 + _KEEP_FULL_OBS * 2:
        del out[1]  # remove the oldest post-task turn
    return out


def call_llm(messages: list[dict], temperature: float = 0.0) -> str:
    pruned = _prune_messages(messages)
    full = [{"role": "system", "content": SYSTEM_PROMPT}] + pruned

    for attempt, default_wait in enumerate(_LLM_RETRY_WAITS):
        try:
            resp = llm_client.chat.completions.create(
                model=MODEL, messages=full,
                max_tokens=MAX_TOKENS, temperature=temperature,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            err = str(e)
            if "rate_limit" not in err.lower() and "429" not in err:
                raise
            m = re.search(r"(?:retry.after|please try again in)[^\d]*(\d+(?:\.\d+)?)", err, re.I)
            wait = max(float(m.group(1)) + 2, default_wait) if m else default_wait
            print(f"  [openrouter] rate limited ({attempt+1}/{len(_LLM_RETRY_WAITS)}), waiting {wait:.0f}s")
            time.sleep(wait)
    raise RuntimeError(f"OpenRouter: exhausted retries for model={MODEL}")


# ── code helpers ──────────────────────────────────────────────────────────────
def extract_code(text: str) -> str:
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    if blocks:
        return blocks[-1].strip()
    stripped = text.strip()
    if re.match(r"^(apis\.|print\(|import |for |if |def |[a-z_]\w*\s*=)", stripped):
        return stripped
    return ""


def is_error_output(output: str) -> bool:
    lower = output.lower()
    if lower.startswith("execution failed") or lower == "no code available to execute.":
        return True
    return any(k in lower for k in (
        "traceback", "error:", "exception:",
        "syntaxerror", "nameerror", "typeerror", "valueerror",
        "attributeerror", "keyerror", "indexerror",
        "permissionerror", "runtimeerror", "assertionerror",
        "is not allowed",
    ))


def build_error_hint(code: str, output: str) -> str:
    lower = output.lower()

    if "401" in output or "not authorized" in lower or "access token is missing" in lower:
        app_m = re.search(r"apis\.(\w+)\.", code)
        app = app_m.group(1) if app_m else "<app>"
        uname = "supervisor_profile['phone_number']" if app == "phone" else "supervisor_profile['email']"
        return (
            f"\n\n[HINT: 401 Unauthorized — you have not logged into `{app}` yet, "
            f"or passed the wrong token. Fix:\n"
            f"  {app}_token = apis.{app}.login(\n"
            f"      username={uname},\n"
            f"      password=supervisor_passwords['{app}'],\n"
            f"  )['access_token']\n"
            f"Then pass access_token={app}_token to every {app} API call.]"
        )

    if "422" in output or "field required" in lower or "validation error" in lower:
        return ("\n\n[HINT: 422 — a required parameter is missing or misnamed (you likely guessed "
                "the wrong keyword, e.g. to=/body= instead of email_addresses=/message=/phone_number=). "
                "Run print(apis.api_docs.show_api_doc(app_name='<app>', api_name='<api>')) for exact param names.]")

    if "409" in output and "does not exist" in lower:
        return ("\n\n[HINT: 409 'does not exist' — the recipient/target value didn't match a real user, OR "
                "you passed it under the wrong keyword so it arrived empty. Check the exact param name with "
                "show_api_doc (e.g. phone.send_text_message needs phone_number=, not to=), and confirm the value "
                "came from a printed response.]")

    if "takes 0 positional arguments" in lower or "positional argument" in lower:
        return ("\n\n[HINT: You passed POSITIONAL arguments. AppWorld APIs accept keyword args ONLY — "
                "rewrite as apis.app.method(param=value, ..., access_token=token).]")

    no_api_m = re.search(r"No API named '(\w+)' found in the (\w+) app", output)
    if no_api_m:
        bad, app = no_api_m.group(1), no_api_m.group(2)
        extra = ""
        if app == "gmail" and "search" in bad:
            extra = " To search gmail use show_inbox_threads(query=..., access_token=...)."
        return (f"\n\n[HINT: `{app}.{bad}` does not exist.{extra} "
                f"Run print(apis.api_docs.show_api_descriptions(app_name='{app}')) for the real names.]")

    if "is not allowed" in lower:
        return ("\n\n[HINT: Disallowed module/function used. "
                "Use apis.file_system for file ops instead of open()/os/subprocess.]")

    if "timed out" in lower:
        return ("\n\n[HINT: Execution timed out (100s limit). "
                "Too many API calls in one cell — use a search API or split into smaller steps.]")

    if "writing to os file system is disabled" in lower:
        return ("\n\n[HINT: OS filesystem writes are blocked. "
                "Use apis.file_system.create_file(...) / update_file(...) instead.]")

    attr_m = re.search(r"AttributeError.*?has no attribute '(\w+)'", output)
    if attr_m:
        bad = attr_m.group(1)
        app_m = re.search(rf"apis\.(\w+)\.{re.escape(bad)}", code)
        app = app_m.group(1) if app_m else None
        if app:
            return (f"\n\n[HINT: `{app}.{bad}` does not exist. "
                    f"Run: print(apis.api_docs.show_api_descriptions(app_name='{app}'))]")
        return (f"\n\n[HINT: `{bad}` does not exist. "
                "Run apis.api_docs.show_api_descriptions(app_name='<app>') to find the correct name.]")

    key_m = re.search(r"KeyError: '(\w+)'", output)
    if key_m:
        bad = key_m.group(1)
        extra = ""
        if bad in ("id", "messageId") or "title" in bad:
            extra = (" AppWorld uses <entity>_id (e.g. draft_id, order_id, product_id) and "
                     "'name', not 'id'/'title'.")
        return (f"\n\n[HINT: KeyError '{bad}' — that key isn't in the response.{extra} "
                "Run print(list(obj.keys())) and use a key that actually appears.]")

    if "indexerror" in lower or "list index out of range" in lower:
        return ("\n\n[HINT: IndexError — list is empty or shorter than expected. "
                "Print the list before indexing; your filter may have returned nothing.]")

    if "typeerror" in lower:
        return ("\n\n[HINT: TypeError — wrong type passed to a parameter. "
                "Print the variable and its type() before using it.]")

    return ""


# ── bootstrap (run setup boilerplate once, before the LLM loop) ─────────────────
def bootstrap_setup(world: AppWorld, allowed_apps: list[str]) -> list[str]:
    """Pre-run profile/passwords/login in the persistent namespace so the model
    starts at the actual task instead of spending 1-2 turns (and any 401 recovery
    turns) on boilerplate. Returns the list of apps whose token is ready."""
    apps = [a for a in allowed_apps if a not in _INTERNAL_APPS]
    lines = [
        "supervisor_profile = apis.supervisor.show_profile()",
        "supervisor_passwords = {p['account_name']: p['password'] "
        "for p in apis.supervisor.show_account_passwords()}",
        "_ready_tokens = []",
    ]
    # phone authenticates by phone_number, not email; try both usernames per app so
    # one bad guess never leaves a token un-created (each is independent).
    for app in apps:
        lines.append(
            f"for _u in [supervisor_profile.get('phone_number'), supervisor_profile['email']] "
            f"if '{app}' == 'phone' else [supervisor_profile['email'], supervisor_profile.get('phone_number')]:\n"
            f"    try:\n"
            f"        {app}_token = apis.{app}.login("
            f"username=_u, password=supervisor_passwords['{app}'])['access_token']\n"
            f"        _ready_tokens.append('{app}')\n"
            f"        break\n"
            f"    except Exception:\n"
            f"        continue"
        )
    lines.append(
        "print('BOOTSTRAP OK — ready tokens: ' + ', '.join(f'{a}_token' for a in _ready_tokens))"
    )
    try:
        out = str(world.execute("\n".join(lines)))
    except Exception as e:
        print(f"  [bootstrap] failed: {e}")
        return []
    m = re.search(r"ready tokens: (.+)", out)
    ready_str = m.group(1).strip() if m else ""
    ready = [t.replace("_token", "") for t in ready_str.split(", ") if t.endswith("_token")]
    if ready:
        print(f"  [bootstrap] pre-logged into: {', '.join(ready)}")
    return ready


# ── solve loop ────────────────────────────────────────────────────────────────
def solve(world: AppWorld, task_id: str) -> bool:
    sup         = world.task.supervisor
    instruction = world.task.instruction
    allowed_apps = world.task.allowed_apps

    # Understand the relevant APIs BEFORE acting: HydraDB semantic retrieval returns the
    # exact params + response schemas for the APIs most relevant to this instruction.
    api_docs = retrieve_api_docs(instruction)
    memories = retrieve_task_memories(instruction)
    ready_tokens = bootstrap_setup(world, allowed_apps)

    messages: list[dict] = [{
        "role": "user",
        "content": build_task_prompt(
            instruction, sup, allowed_apps, api_docs=api_docs, memories=memories,
            ready_tokens=ready_tokens
        ),
    }]

    consecutive_errors = 0
    budget_warned      = False
    last_code          = ""
    fail_streak        = 0   # error turns since last clean execution (does not reset like consecutive_errors)
    repeat_count       = 0   # times the current code has repeated

    for step in range(MAX_INTERACTIONS):
        steps_left = MAX_INTERACTIONS - step - 1

        if step > 0:
            time.sleep(STEP_DELAY)

        temperature = 0.4 if consecutive_errors >= 5 else 0.0
        reply = call_llm(messages, temperature=temperature)
        code  = extract_code(reply)

        if not code:
            feedback = ("Output:\n[No code block found. Output a `Thought:` line "
                        "then exactly ONE ```python ... ``` block.]")
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": feedback})
            consecutive_errors += 1
            fail_streak += 1
            if fail_streak >= MAX_FAIL_STREAK:
                print(f"  ✗ aborting — {fail_streak} failing turns without progress (no code)")
                return False
            continue

        raw = str(world.execute(code))
        truncated = raw[:MAX_OUTPUT_CHARS]
        if len(raw) > MAX_OUTPUT_CHARS:
            truncated += f"\n... [truncated — {len(raw) - MAX_OUTPUT_CHARS} chars]"

        print(f"  step {step+1}/{MAX_INTERACTIONS}: {len(code)}ch -> {truncated[:120]!r}")

        # Detect silent fetch — model called an API but forgot print()
        if truncated.strip() == "Execution successful." and re.search(r"\bapis\.\w+\.\w+\(", code):
            has_print = bool(re.search(r"\bprint\s*\(", code))
            stores_result = bool(re.search(r"^\s*\w+\s*=\s*apis\.", code, re.M))
            if not has_print and stores_result:
                truncated += ("\n\n[HINT: You fetched data but forgot print(). "
                              "Add print() around every API result so you can use the data next turn.]")

        if is_error_output(truncated):
            consecutive_errors += 1
            fail_streak += 1
            hint = build_error_hint(code, truncated)
            if hint:
                truncated += hint
            elif consecutive_errors == 3:
                truncated += ("\n\n[HINT: 3 consecutive errors — fix the exact failing line, "
                              "check api_doc for correct names. Do NOT repeat the same code.]")
            elif consecutive_errors >= 5:
                truncated += ("\n\n[HINT: 5 errors — try a completely different approach. "
                              "Print apis.api_docs.show_api_doc(...) for the API you're stuck on.]")
                consecutive_errors = 0
        else:
            consecutive_errors = 0
            fail_streak = 0  # clean execution → real progress, reset the abort counter

        feedback = f"Output:\n{truncated}"

        repeat_count = repeat_count + 1 if (code == last_code and code) else 0
        if code == last_code and code:
            feedback += ("\n\n[STUCK: Same code as last turn — same result guaranteed. "
                         "You MUST change your approach entirely.]")
        last_code = code

        if step == 2:
            feedback += "\n\n[Reminder: prefer search_X() over fetching all items in a loop.]"

        if steps_left <= 8 and not budget_warned:
            budget_warned = True
            feedback += f"\n\n[{steps_left} steps left — wrap up and call complete_task soon.]"
        elif steps_left <= 2:
            if classify_task(instruction) == "question":
                feedback += '\n\n[URGENT: Call apis.supervisor.complete_task(answer="...") NOW.]'
            else:
                feedback += "\n\n[URGENT: Call apis.supervisor.complete_task() NOW.]"

        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": feedback})

        if world.task_completed():
            print(f"  ✓ completed at step {step+1}")
            store_task_memory(task_id, instruction, extract_apis_used(messages), step + 1)
            return True

        # Early stop: the agent is flailing — bail out instead of burning the whole budget.
        if fail_streak >= MAX_FAIL_STREAK:
            print(f"  ✗ aborting at step {step+1} — {fail_streak} failing turns without progress")
            return False
        if repeat_count >= MAX_CODE_REPEATS - 1:
            print(f"  ✗ aborting at step {step+1} — same code repeated {repeat_count + 1}x with no progress")
            return False

    print("  ✗ hit MAX_INTERACTIONS without completion")
    return False


# ── entry point ───────────────────────────────────────────────────────────────
def main() -> None:
    task_ids = load_task_ids(DATASET)
    if SKIP_TASKS:
        task_ids = task_ids[SKIP_TASKS:]
    if MAX_TASKS:
        task_ids = task_ids[:MAX_TASKS]

    total = len(task_ids)
    print(f"Running '{EXPERIMENT}' on {total} '{DATASET}' tasks")
    print(f"  model={MODEL}")
    print(f"  hydra={'enabled' if HYDRA_KEY else 'disabled (no HYDRA_DB_API_KEY)'}")

    success = failed = errors = 0

    for i, task_id in enumerate(task_ids, 1):
        print(f"\n[{i}/{total}] {task_id}")
        _real_open = builtins.open
        try:
            with AppWorld(task_id=task_id, experiment_name=EXPERIMENT) as world:
                if solve(world, task_id):
                    success += 1
                else:
                    failed += 1
        except Exception as e:
            print(f"  ! error: {e}")
            errors += 1
        finally:
            builtins.open = _real_open

        done = success + failed + errors
        print(f"  score: {success}/{done} ({100*success/done:.0f}%) — {failed} failed, {errors} errored")

        if i < total:
            print(f"  [cooldown] {TASK_DELAY}s...")
            time.sleep(TASK_DELAY)

    print(f"\n{'='*50}")
    print(f"Final: {success}/{total} ({100*success/total:.1f}%)")
    print(f"       {failed} failed, {errors} errored")
    print(f"Results in ./experiments/outputs/{EXPERIMENT}/")


if __name__ == "__main__":
    main()
