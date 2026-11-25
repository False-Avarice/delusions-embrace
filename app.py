from flask import Flask, jsonify, render_template, request

from game_engine import GameEngine

app = Flask(__name__)
engine = GameEngine()
MAX_CHOICES_PER_RUN = 10


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start_game():
    scene = engine.process_step(engine.get_initial_state())
    return jsonify(**scene, choice_history=[])


@app.route('/choice', methods=['POST'])
def make_choice():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Expected a JSON object."), 400

    history = data.get("choice_history")
    if not isinstance(history, list) or len(history) > MAX_CHOICES_PER_RUN:
        return jsonify(error="Invalid choice history."), 400

    # Rebuild the scene from this page's choices so retries are independent of
    # cookies, other tabs, and the lifetime of the server process.
    state = engine.get_initial_state()
    scene = engine.process_step(state)
    for index in history:
        if state["current_step"] == "restart" or not valid_choice(index, scene):
            return jsonify(error="Invalid choice history."), 400
        scene = engine.process_step(state, index)

    index = data.get("choice_index")
    if not valid_choice(index, scene):
        return jsonify(error="Invalid choice for this scene."), 400

    restarting = state["current_step"] == "restart"
    scene = engine.process_step(state, index)
    return jsonify(**scene, choice_history=[] if restarting else [*history, index])


def valid_choice(index, scene):
    return type(index) is int and 0 <= index < len(scene["choices"])


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=False)
