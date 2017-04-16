import os


get_abs_path = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), p))


MIDI_DIR = get_abs_path("../data/raw/")
SEQUENCE_FILE = get_abs_path("../data/interim/notesequences.tfrecord")
OUTPUT_DIR = get_abs_path("../data/processed")
MODEL_DIR = get_abs_path("../models")

GENERATED_DIR = get_abs_path("../data/generated")
