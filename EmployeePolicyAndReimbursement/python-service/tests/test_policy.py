from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json()['status'] == 'ok'


def test_answer_policy_question():
    payload = {"question": "What is my annual certification reimbursement limit?", "as_of": "2026-09-21"}
    resp = client.post('/answer', json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body['status'] == 'ANSWERED'
    assert 'INR 25000' in body['answer']
    assert len(body['citations']) >= 1
