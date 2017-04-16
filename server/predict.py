import os
import time
import tempfile
import pretty_midi
import tensorflow as tf
import magenta
from magenta.models.melody_rnn import melody_rnn_config_flags
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.protobuf import generator_pb2
from magenta.protobuf import music_pb2


BUNDLE_NAME = os.getenv("MAGENTA_MODEL", "attention_rnn")
STEPS_PER_QUARTER = 4


def _steps_to_seconds(steps, qpm):
    return steps * 60.0 / qpm / STEPS_PER_QUARTER


def make_generator(bundle_name):
    model_path = os.path.join(os.path.dirname(__file__), "../models/" + bundle_name + ".mag")
    hparams_path = os.path.join(os.path.dirname(__file__), "../models/" + bundle_name + ".hparams")

    if tf.gfile.Exists(hparams_path):
        with tf.gfile.Open(hparams_path) as f:
            config, hparams = f.readline().split("\t")
        melody_rnn_config_flags.FLAGS.config = config
        melody_rnn_config_flags.FLAGS.hparams = hparams
        config = melody_rnn_config_flags.config_from_flags()
    elif bundle_name in melody_rnn_model.default_configs:
        config = melody_rnn_model.default_configs[bundle_name]
    else:
        raise Exception("can not define the model config.")
 
    generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
        model=melody_rnn_model.MelodyRnnModel(config),
        details=config.details,
        steps_per_quarter=STEPS_PER_QUARTER,
        bundle=magenta.music.read_bundle_file(model_path))
    
    return generator


generator = make_generator(BUNDLE_NAME)


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
