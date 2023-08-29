"""
Engie-GEM Powerplant coding challenge
Main entrypoint script
"""

from flask import Flask, Response, request
from merit.merit import MeritOrder
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s]: %(message)s')
app = Flask(__name__)


@app.route('/')
def index():
    """
    The home route in this case is unused, so we will return a 204 "No Content"
    :return: HTTP response 204
    """

    return Response(status=204)


@app.route('/productionplan', methods=['POST'])
def productionplan():
    if request.method == 'POST':
        payload = request.get_json()
        merit_plan = MeritOrder(payload)
        return merit_plan.calculate()
    else:
        return 'Method invalid'


if __name__ == "__main__":
    try:
        logging.info(f'Starting application...')
        app.run(host="0.0.0.0", port=8888, debug=True)
    except Exception as e:
        logging.error(f'There was an issue starting the app. Error: {e}')
