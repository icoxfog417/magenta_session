import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import tensorflow as tf
import magenta
import magenta.models.melody_rnn.melody_rnn_train as mt
from magenta.models.melody_rnn import melody_rnn_config_flags
from magenta.models.shared import events_rnn_graph
from magenta.models.shared import events_rnn_train
import scripts.target as tgt


def main(unused_argv):
    tf.logging.set_verbosity(mt.FLAGS.log)
    data_dir = tgt.OUTPUT_DIR
    train_dir = os.path.join(tgt.MODEL_DIR, "logdir/train")
    if not os.path.exists(train_dir):
        tf.gfile.MakeDirs(train_dir)

    config = mt.melody_rnn_config_flags.config_from_flags()

    if not mt.FLAGS.eval:
        train_file = tf.gfile.Glob(os.path.join(data_dir, "training_melodies.tfrecord"))
        tf.logging.info("Train dir: %s", train_dir)
        with tf.gfile.Open(os.path.join(train_dir, "hparams"), mode="w") as f:
            f.write("\t".join([mt.FLAGS.config, mt.FLAGS.hparams]))

        graph = events_rnn_graph.build_graph("train", config, train_file)
        events_rnn_train.run_training(
            graph, train_dir, mt.FLAGS.num_training_steps, mt.FLAGS.summary_frequency, checkpoints_to_keep=mt.FLAGS.num_checkpoints)

    else:
        eval_file = tf.gfile.Glob(os.path.join(data_dir, "eval_melodies.tfrecord"))
        eval_dir = os.path.join(tgt.MODEL_DIR, "logdir/eval")
        if not os.path.exists(eval_dir):
            tf.gfile.MakeDirs(eval_dir)
        tf.logging.info("Eval dir: %s", eval_dir)
        
        examples = mt.FLAGS.num_eval_examples if mt.FLAGS.num_eval_examples else magenta.common.count_records(eval_file)
        
        if examples >= config.hparams.batch_size:
            num_batches = examples // config.hparams.batch_size
        else:
            config.hparams.batch_size = examples
            num_batches = 1
      
        graph = events_rnn_graph.build_graph("eval", config, eval_file)
        events_rnn_train.run_eval(
            graph, train_dir, eval_dir, num_batches)


def console_entry_point():
  tf.app.run(main)


if __name__ == "__main__":
    console_entry_point()
