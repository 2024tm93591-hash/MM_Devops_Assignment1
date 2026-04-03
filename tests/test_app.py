import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gym import app


def get_auth_token(client):
    response = client.post('/login', json={'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 200
    return response.get_json()['token']


def test_member_crud_and_auth_flow():
    client = app.test_client()
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}

    # Add member
    response = client.post('/members', json={'name': 'John Doe', 'email': 'john@example.com', 'plan': 'Premium'}, headers=headers)
    assert response.status_code == 201
    member_id = response.get_json()['id']

    # List members
    response = client.get('/members', headers=headers)
    assert response.status_code == 200
    assert any(m['id'] == member_id for m in response.get_json())

    # Delete member
    response = client.delete(f'/members/{member_id}', headers=headers)
    assert response.status_code == 200

    # Ensure removed
    response = client.get('/members', headers=headers)
    assert all(m['id'] != member_id for m in response.get_json())


def test_bmi_endpoint():
    client = app.test_client()
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}

    response = client.post('/bmi', json={'height': 1.8, 'weight': 75}, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'bmi' in data and 'category' in data
