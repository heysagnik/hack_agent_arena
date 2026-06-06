"""
hydra_setup.py — Run ONCE before your benchmark run.

Reads AppWorld API docs directly from the installed package (no AppWorld
environment needed) and ingests them into HydraDB for semantic retrieval.

Usage:
    python hydra_setup.py
"""

import os
import json
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from hydra_db import HydraDB
from appworld.collections.api_docs import prepare_api_docs, get_all_apps

HYDRA_TENANT     = os.environ.get("HYDRA_TENANT", "appworld-v1")
HYDRA_MEM_TENANT = os.environ.get("HYDRA_MEM_TENANT", "appworld-task-memory")
HYDRA_API_KEY    = os.environ["HYDRA_DB_API_KEY"]

hydra = HydraDB(token=HYDRA_API_KEY)


def provision_tenant():
    try:
        hydra.tenants.create(
            tenant_id=HYDRA_TENANT,
            tenant_metadata_schema=[
                {"name": "app_name", "data_type": "VARCHAR", "enable_match": True, "enable_dense_embedding": False, "enable_sparse_embedding": False},
                {"name": "api_name", "data_type": "VARCHAR", "enable_match": True, "enable_dense_embedding": False, "enable_sparse_embedding": False},
                {"name": "doc_type", "data_type": "VARCHAR", "enable_match": True, "enable_dense_embedding": False, "enable_sparse_embedding": False},
            ],
        )
        print(f"Tenant '{HYDRA_TENANT}' created. Waiting for readiness...")
        for _ in range(60):
            status = hydra.tenants.status(tenant_id=HYDRA_TENANT)
            if status.data.infra.ready_for_ingestion:
                print("Tenant ready.")
                return
            time.sleep(3)
        raise RuntimeError("Tenant never became ready")
    except Exception as e:
        err = str(e)
        if "already exists" in err.lower() or "409" in err:
            print(f"Tenant '{HYDRA_TENANT}' already exists — skipping creation.")
        else:
            raise


def collect_api_docs() -> list[dict]:
    """Read all API docs from the installed appworld package."""
    docs = []
    apps = get_all_apps()
    print(f"Collecting API docs for {len(apps)} apps: {apps}")

    for app in apps:
        try:
            api_list = prepare_api_docs(app)
            for entry in api_list:
                api_name = entry.get("api_name", "unknown")
                text = (
                    f"APP: {app} | API: {api_name}\n"
                    f"Path: {entry.get('path', '')} [{entry.get('method', '')}]\n"
                    f"Description: {entry.get('description', '')}\n"
                    f"Parameters: {json.dumps(entry.get('parameters', []), indent=2)}\n"
                    f"Response schemas: {json.dumps(entry.get('response_schemas', {}), indent=2)}"
                )
                docs.append({
                    "id": f"{app}__{api_name}",
                    "tenant_id": HYDRA_TENANT,
                    "sub_tenant_id": "default",
                    "title": f"{app} / {api_name}",
                    "type": "document",
                    "content": {"text": text},
                    "tenant_metadata": {
                        "app_name": app,
                        "api_name": api_name,
                        "doc_type": "api_doc",
                    },
                })
            print(f"  {app}: {len(api_list)} endpoints")
        except Exception as e:
            print(f"  Warning: failed on '{app}': {e}")

    return docs


def ingest_docs(docs: list[dict]):
    if not docs:
        print("No docs to ingest.")
        return

    # HydraDB has a max per request — batch into chunks of 100
    BATCH = 100
    all_source_ids = []

    for i in range(0, len(docs), BATCH):
        batch = docs[i:i + BATCH]
        print(f"Ingesting batch {i // BATCH + 1} ({len(batch)} docs)...")
        response = hydra.context.ingest(
            type="knowledge",
            tenant_id=HYDRA_TENANT,
            app_knowledge=json.dumps(batch),
        )
        ids = [item.id for item in response.data.results]
        all_source_ids.extend(ids)

    print(f"All {len(all_source_ids)} sources submitted. Polling for indexing completion...")

    POLL_BATCH = 20  # poll a small sample to gauge progress
    sample_ids = all_source_ids[:POLL_BATCH]

    for attempt in range(120):
        time.sleep(5)
        try:
            status_resp = hydra.context.status(tenant_id=HYDRA_TENANT, ids=sample_ids)
            statuses = [s.indexing_status for s in status_resp.data.statuses]
            done = all(s in ("graph_creation", "completed") for s in statuses)
            counts = {s: statuses.count(s) for s in set(statuses)}
            print(f"  [{attempt + 1}] sample of {len(sample_ids)}: {counts}")
            if done:
                print("Sample fully indexed — all docs should be searchable.")
                return
        except Exception as e:
            print(f"  [{attempt + 1}] poll error (retrying): {e}")

    print("Warning: indexing timed out — docs may not be fully searchable.")


def provision_memory_tenant():
    """Create the memory tenant that agent.py writes successful task patterns into."""
    try:
        hydra.tenants.create(tenant_id=HYDRA_MEM_TENANT)
        print(f"Memory tenant '{HYDRA_MEM_TENANT}' created. Waiting for readiness...")
        for _ in range(60):
            status = hydra.tenants.status(tenant_id=HYDRA_MEM_TENANT)
            if status.data.infra.ready_for_ingestion:
                print("Memory tenant ready.")
                return
            time.sleep(3)
        raise RuntimeError("Memory tenant never became ready")
    except Exception as e:
        err = str(e)
        if "already exists" in err.lower() or "409" in err:
            print(f"Memory tenant '{HYDRA_MEM_TENANT}' already exists — skipping.")
        else:
            raise


def main():
    print("── Step 1: Knowledge tenant (API docs) ──")
    provision_tenant()
    docs = collect_api_docs()
    print(f"\nTotal: {len(docs)} API doc chunks to index")
    ingest_docs(docs)

    print("\n── Step 2: Memory tenant (task patterns) ──")
    provision_memory_tenant()

    print(f"\nDone. Run: python agent.py")


if __name__ == "__main__":
    main()
