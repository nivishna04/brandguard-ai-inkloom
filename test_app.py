from fastapi.testclient import TestClient
import main, os
c = TestClient(main.app)
H = lambda r: {"X-Role": r}
T = "Brewline cold brew is the No. 1 drink in India! Only $3.99, so cheap!! Try it today."
d = c.post("/api/drafts", json={"text": T}, headers=H("creator")).json()
cats = sorted({f["category"] for f in d["findings"]}); print("categories:", cats)
assert {"unsupported_claim", "prohibited_term", "outdated_fact", "missing_required", "tone"} <= set(cats)
assert c.post("/api/drafts", json={"text": T}, headers=H("approver")).status_code == 403
assert c.post("/api/drafts", json={"text": " "}, headers=H("creator")).status_code == 400
i = d["id"]
f = next(f for f in d["findings"] if f["category"] == "outdated_fact")
d = c.post(f"/api/drafts/{i}/findings/{f['id']}", json={"action": "accept"}, headers=H("creator")).json()
assert "$4.50" in d["revisions"][-1]["text"]
f = next(f for f in d["findings"] if f["category"] == "tone")
assert c.post(f"/api/drafts/{i}/findings/{f['id']}", json={"action": "dismiss"}, headers=H("creator")).status_code == 400
c.post(f"/api/drafts/{i}/findings/{f['id']}", json={"action": "dismiss", "reason": "Intended"}, headers=H("creator"))
c.post(f"/api/drafts/{i}/submit", headers=H("creator"))
assert c.post(f"/api/drafts/{i}/decision", json={"decision": "approve"}, headers=H("reviewer")).status_code == 403
assert c.post(f"/api/drafts/{i}/decision", json={"decision": "approve"}, headers=H("approver")).status_code == 400  # open high findings
r = c.post(f"/api/drafts/{i}/decision", json={"decision": "approve", "rationale": "Legal cleared claim"}, headers=H("approver")).json()
print("final status:", r["status"], "| audit entries:", len(c.get("/api/audit").json()))
assert r["status"] == "Approved"
print("ALL TESTS PASSED")
