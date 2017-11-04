import os
import sys
import json
import pretty_midi
import predict as predictor
from flask import Flask
from flask import render_template, send_file, request

static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
app = Flask(__name__, template_folder=static_path, static_folder=static_path)

@app.route("/predict", methods=["POST"])
def predict():
    notes = json.loads(request.get_data())
    if sys.version_info.major <= 2:
        from cStringIO import StringIO
        note_stream = StringIO("".join(chr(n) for n in notes))
    else:
        from io import BytesIO
        note_stream = BytesIO("".join(chr(n) for n in notes).encode("latin1"))

    midi_data = pretty_midi.PrettyMIDI(note_stream)
    duration = float(request.args.get("duration"))  #seconds
    generated = predictor.generate_midi(midi_data, duration)
    return send_file(generated, attachment_filename="output.mid", 
        mimetype="audio/midi", as_attachment=True)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", model_name=predictor.BUNDLE_NAME)


@app.route("/test", methods=["GET", "POST"])
def test():
    return render_template("test.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as ex:
        print(ex)
