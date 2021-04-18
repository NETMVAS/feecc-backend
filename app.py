from flask import Flask, request
from flask_restful import Api, Resource
import typing as tp
import requests

# global variables
agent_api_address: str = "http://127.0.0.1:8080/api"
current_state: int = 0  # number of the state system is in currently. Ranges from 0 to 3 (refer to states description).

app = Flask(__name__)
api = Api(app)


def update_agent_state(priority: int) -> int:
    """post an updated system state to the backend to keep it sync with the local state"""

    change_agent_state = requests.post(
        url=f"{agent_api_address}/state-update",
        json={
            "change_state_to": current_state,
            "priority": priority
        }
    )

    return change_agent_state.status_code


# REST API request handlers
class CurrentState(Resource):
    """returns current state of the system to the frontend as it is long polling the backend"""

    def get(self) -> tp.Dict[str, int]:
        response = {"state_no": current_state}
        return response


class FormHandler(Resource):
    """accepts a filled form from the frontend and reroutes it to the agent"""

    def post(self) -> int:

        # parse the form data
        form_data = request.get_json()

        # send the form to the agent
        relay_the_form = requests.post(
            url=f"{agent_api_address}/form-handler",
            json=form_data
        )

        # change own state and tell the agent to change it's state
        if relay_the_form.ok:
            global current_state
            current_state = 2
            update_agent_state(priority=2)

        return 200


class StateUpdateHandler(Resource):
    """handles a state update request"""

    def post(self) -> int:
        # parse the form data
        data = request.get_json()

        # change own state to the one specified by the sender
        global current_state
        current_state = data["change_state_to"]

        return 200


# REST API endpoints
api.add_resource(CurrentState, "/api/state")
api.add_resource(FormHandler, "/api/form-handler")
api.add_resource(StateUpdateHandler, "/api/state-update")


@app.route("/")
def index():
    """returns an index page to the client"""

    return "Index page here"


if __name__ == "__main__":
    app.run(debug=False)
