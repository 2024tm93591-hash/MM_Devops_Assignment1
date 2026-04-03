from gym import app   # or your main file name

def test_home():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200