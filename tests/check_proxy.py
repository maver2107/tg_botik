import requests

url = "https://jsonplaceholder.typicode.com"


def test_proxy():
    respomse = requests.get(url)
    assert respomse.status_code == 200
