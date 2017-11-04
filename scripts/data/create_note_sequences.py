# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import tensorflow as tf
from magenta.scripts.convert_dir_to_note_sequences import note_sequence_io
from magenta.scripts.convert_dir_to_note_sequences import convert_directory
import scripts.target as tgt


def main():
    output_dir = os.path.dirname(tgt.SEQUENCE_FILE)
    if not os.path.exists(output_dir):
        tf.gfile.MakeDirs(output_dir)

    convert_directory(tgt.MIDI_DIR, tgt.SEQUENCE_FILE, recursive=True)


if __name__ == '__main__':
    tf.logging.set_verbosity("INFO")
    main()
