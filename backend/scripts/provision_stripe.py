import os
import json
import urllib.request
import urllib.error

base = os.environ["INTEGRATION_PROXY_URL"]
job_id = "6f51e96f-16c0-4f46-848c-848a0b79be23"
key = "sk-emergent-25b16F44f5155C605D"

req = urllib.request.Request(
    base + "/stripe/sandboxes",
    data=json.dumps({"job_id": job_id}).encode(),
    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req) as r:
        sandbox = json.load(r)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"PROVISIONING FAILED {e.code}: {body}")
    raise SystemExit(1)

print(json.dumps({
    "sandbox_secret_key": sandbox.get("sandbox_secret_key"),
    "sandbox_publishable_key": sandbox.get("sandbox_publishable_key"),
    "sandbox_account_id": sandbox.get("sandbox_account_id"),
    "onboarding_url": sandbox.get("onboarding_url"),
    "preview_webhook_secret": sandbox.get("preview_webhook_secret"),
}, indent=2))
