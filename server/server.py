import os
import sys
if sys.version_info.major <= 2:
    from cStringIO import StringIO
else:
    from io import StringIO
import json
import pretty_midi
from predict import generate_midi
from flask import Flask
from flask import render_template, send_file, request

static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static"))
app = Flask(__name__, template_folder=static_path, static_folder=static_path)

@app.route("/predict", methods=["POST"])
def predict():
    notes = json.loads(request.get_data())
    midi_data = pretty_midi.PrettyMIDI(StringIO("".join(chr(n) for n in notes)))
    duration = float(request.args.get("duration"))  #seconds
    generated = generate_midi(midi_data, duration)
    return send_file(generated, attachment_filename="output.mid", 
        mimetype="audio/midi", as_attachment=True)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/test", methods=["GET", "POST"])
def test():
    return render_template("test.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
