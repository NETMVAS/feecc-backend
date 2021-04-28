from flask import Flask, request, Response, render_template
from flask_restful import Api, Resource
import typing as tp
import requests
import logging
import json

# set up logging
logging.basicConfig(
    level=logging.DEBUG,
    # filename="backend.log",
    format="%(asctime)s %(levelname)s: %(message)s"
)

logging.info('Backend started')

# global variables
agent_api_address: str = "http://127.0.0.1:5000/api"
current_state: int = 0  # number of the state system is in currently. Ranges from 0 to 3 (refer to states description).
valid_states = [0, 1, 2, 3]

app = Flask(__name__)
api = Api(app)


def update_agent_state(priority: int) -> int:
    """post an updated system state to the agent to keep it synced with the local state"""

    logging.info(f"Changing agent state to {current_state}")
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
        global current_state

        logging.debug(
            f"Received a request for current state. Responding with {current_state}"
        )

        response = {"state_no": current_state}
        return response


class FormOptions(Resource):
    """returns contents of the form_options.json file for the frontend to make use of"""

    def get(self):
        logging.info(f"Received a request for form options.")

        try:
            with open("form_options.json", "r") as file:
                form_options = json.load(file)

            response: tp.Dict[str, tp.Dict[str, tp.Any]] = form_options
            logging.info("served form options successfully")

            return response

        except Exception as E:
            logging.critical(f"Failed to serve form options:\n{E}")

            return 500


class FormHandler(Resource):
    """accepts a filled form from the frontend and reroutes it to the agent"""

    def post(self) -> int:
        logging.info(
            f"Received a form. Relaying to the agent."
        )

        # parse the form data
        form_data = request.get_json()

        # send the form to the agent
        relay_the_form = requests.post(
            url=f"{agent_api_address}/form-handler",
            json=form_data
        )

        global current_state

        # change own state and tell the agent to change it's state
        if relay_the_form.ok:
            current_state = 2
            update_agent_state(priority=2)

            logging.info(
                f"Form relay success. Current state: {current_state}"
            )

        else:
            logging.error(
                f"""
                Form relay failed. 
                Form: {form_data},
                Request status: {relay_the_form.status_code}
                Current state: {current_state}
                """
            )

        return 200


class StateUpdateHandler(Resource):
    """handles a state update request"""

    def post(self):
        logging.info(
            f"Received a request to update the state."
        )

        # parse the request data
        data = request.get_json()

        # validate the request
        global valid_states
        global current_state

        if not data["change_state_to"] in valid_states:
            logging.warning(
                f"Invalid state transition: '{data['change_state_to']}' is not a valid state. Staying at {current_state}"
            )

            return Response(
                response='{"status": 406, "msg": "invalid state"}',
                status=406
            )

        # change own state to the one specified by the sender
        current_state = data["change_state_to"]

        logging.info(
            f"Successful state transition to {data['change_state_to']}"
        )

        return 200


# REST API endpoints
api.add_resource(CurrentState, "/api/state")
api.add_resource(FormOptions, "/api/form-options")
api.add_resource(FormHandler, "/api/form-handler")
api.add_resource(StateUpdateHandler, "/api/state-update")


@app.route("/")
def index():
    """returns an index page to the client"""

    logging.info("Index page served")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
