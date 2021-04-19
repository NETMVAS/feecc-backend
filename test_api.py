import requests

backend_api_address: str = "http://127.0.0.1:5000/api"


def current_state() -> int:
    """get current state number"""

    _current_state = requests.get(url=f"{backend_api_address}/state")
    return _current_state.json()["state_no"]


def change_state(new_state: int, priority: int = 1) -> tuple:
    """switch state"""

    new_state = requests.post(
        url=f"{backend_api_address}/state-update",
        json={
            "change_state_to": new_state,
            "priority": priority
        }
    )
    return new_state.status_code, new_state.json()


# TESTS
def test_init_state():
    assert current_state() == 0


def test_valid_switch1():
    change_state(1)
    assert current_state() == 1


def test_valid_switch2():
    change_state(2)
    assert current_state() == 2


def test_invalid_switch1():
    response = change_state(10)
    assert response[0] == 406
    assert current_state() == 2


def test_invalid_switch2():
    response = change_state("foo")
    assert response[0] == 406
    assert current_state() == 2
