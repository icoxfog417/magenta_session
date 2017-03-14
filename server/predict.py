import os
import time
import tempfile
import pretty_midi

import magenta
from magenta.models.melody_rnn import melody_rnn_config_flags
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.protobuf import generator_pb2
from magenta.protobuf import music_pb2


BUNDLE_NAME = 'attention_rnn'

config = magenta.models.melody_rnn.melody_rnn_model.default_configs[BUNDLE_NAME]
model_file = os.path.join(os.path.dirname(__file__), "../model/" + BUNDLE_NAME + ".mag")
bundle_file = magenta.music.read_bundle_file(os.path.abspath(model_file))
steps_per_quarter = 4

generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
      model=melody_rnn_model.MelodyRnnModel(config),
      details=config.details,
      steps_per_quarter=steps_per_quarter,
      bundle=bundle_file)

def _steps_to_seconds(steps, qpm):
    return steps * 60.0 / qpm / steps_per_quarter

def generate_midi(midi_data, total_seconds=10):
    primer_sequence = magenta.music.midi_io.midi_to_sequence_proto(midi_data)
    # predict the tempo
    if len(primer_sequence.notes) > 4:
        try:
            estimated_tempo = midi_data.estimate_tempo()
            if estimated_tempo > 240:
                qpm = estimated_tempo / 2
            else:
                qpm = estimated_tempo
        except Exception as ex:
            print(ex)
            qpm = 120        
    else:
        qpm = 120
    primer_sequence.tempos[0].qpm = qpm

    generator_options = generator_pb2.GeneratorOptions()
    # Set the start time to begin on the next step after the last note ends.
    last_end_time = (max(n.end_time for n in primer_sequence.notes)
                     if primer_sequence.notes else 0)
    start_time = last_end_time + _steps_to_seconds(1, qpm)
    generator_options.generate_sections.add(
        start_time=start_time, end_time=total_seconds)

    # generate the output sequence
    generated_sequence = generator.generate(primer_sequence, generator_options)

    output = tempfile.NamedTemporaryFile()
    magenta.music.midi_io.sequence_proto_to_midi_file(generated_sequence, output.name)
    output.seek(0)
    return output
