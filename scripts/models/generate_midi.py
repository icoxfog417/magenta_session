import os
import sys
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import tensorflow as tf
import magenta
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_config_flags
from magenta.models.melody_rnn import melody_rnn_sequence_generator
import magenta.models.melody_rnn.melody_rnn_generate as mg
import scripts.target as tgt


def main(unused_argv):
    tf.logging.set_verbosity(mg.FLAGS.log)

    if not mg.FLAGS.bundle_file:
        tf.logging.fatal("--bundle_file is required")
        return

    model_path = os.path.join(tgt.MODEL_DIR, mg.FLAGS.bundle_file + ".mag")
    hparams_path = os.path.join(tgt.MODEL_DIR, mg.FLAGS.bundle_file + ".hparams")

    if tf.gfile.Exists(hparams_path):
        tf.logging.info("Model parameter is read from file: %s", hparams_path)
        with tf.gfile.Open(hparams_path) as f:
            config, hparams = f.readline().split("\t")
    
        melody_rnn_config_flags.FLAGS.config = config
        melody_rnn_config_flags.FLAGS.hparams = hparams
        config = melody_rnn_config_flags.config_from_flags()
    elif mg.FLAGS.bundle_file in melody_rnn_model.default_configs:
        tf.logging.info("Model parameter is set by default")
        config = melody_rnn_model.default_configs[mg.FLAGS.bundle_file]
    else:
        tf.logging.info("Model parameter is read from arguments: %s", mg.FLAGS.hparams)
        config = melody_rnn_config_flags.config_from_flags()
 
    generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
        model=melody_rnn_model.MelodyRnnModel(config),
        details=config.details,
        steps_per_quarter=config.steps_per_quarter,
        bundle=magenta.music.read_bundle_file(model_path))
    
    mg.FLAGS.output_dir = tgt.GENERATED_DIR
    mg.run_with_flags(generator)


def console_entry_point():
  tf.app.run(main)


if __name__ == '__main__':
  console_entry_point()
