# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import tensorflow as tf
from magenta.scripts.convert_dir_to_note_sequences import note_sequence_io
from magenta.scripts.convert_dir_to_note_sequences import convert_directory
import scripts.target as tgt


def main():
    with note_sequence_io.NoteSequenceRecordWriter(tgt.SEQUENCE_FILE) as sequence_writer:
        sequences_written = convert_directory(tgt.MIDI_DIR, "", sequence_writer, True)
        tf.logging.info("Wrote %d NoteSequence protos to '%s'", 
            sequences_written, tgt.SEQUENCE_FILE)


if __name__ == '__main__':
    main()
