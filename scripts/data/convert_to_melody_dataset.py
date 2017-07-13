import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import tensorflow as tf
import magenta.models.melody_rnn.melody_rnn_create_dataset as md
import scripts.target as tgt


def main(unused_argv):
    tf.logging.set_verbosity(md.FLAGS.log)

    config = md.melody_rnn_config_flags.config_from_flags()
    pipeline_instance = md.get_pipeline(config, md.FLAGS.eval_ratio)
    md.pipeline.run_pipeline_serial(
        pipeline_instance,
        md.pipeline.tf_record_iterator(tgt.SEQUENCE_FILE, pipeline_instance.input_type),
        tgt.OUTPUT_DIR)


def console_entry_point():
    tf.app.run(main)


if __name__ == "__main__":
    console_entry_point()
