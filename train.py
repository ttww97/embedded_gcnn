from __future__ import print_function

from six.moves import xrange

import numpy as np
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from lib.model.mnist_chebyshev_gcnn import MNISTChebyshevGCNN
from lib.graph.distortion import perm_batch_of_features

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_float('learning_rate', 0.001, 'Initial learning rate.')
flags.DEFINE_integer('batch_size', 128, 'How many inputs to process at once.')
flags.DEFINE_integer('max_steps', 2000, 'Number of steps to train.')
flags.DEFINE_float('dropout', 0.5, 'Dropout rate (1 - keep probability).')
flags.DEFINE_string('data_dir', 'data/mnist/input',
                    'Directory for storing input data.')
flags.DEFINE_string('train_dir', 'data/mnist/train',
                    'Directory for storing training data.')
flags.DEFINE_string('log_dir', 'data/mnist/summaries',
                    'Summaries log directory.')
flags.DEFINE_integer('save_step', 100,
                     'How many steps to save checkpoint after.')
flags.DEFINE_integer('display_step', 10,
                     'How many steps to print logging after.')
flags.DEFINE_integer('max_degree', 3, 'Maximum Chebyshev polynomial degree.')

mnist = input_data.read_data_sets(FLAGS.data_dir, one_hot=False)

if tf.gfile.Exists(FLAGS.train_dir):
    tf.gfile.DeleteRecursively(FLAGS.train_dir)
if tf.gfile.Exists(FLAGS.log_dir):
    tf.gfile.DeleteRecursively(FLAGS.log_dir)

placeholders = {
    'features':
    tf.placeholder(tf.float32, [FLAGS.batch_size, 976, 1], 'features'),
    'labels':
    tf.placeholder(tf.int32, [FLAGS.batch_size], 'labels'),
    'dropout':
    tf.placeholder(tf.float32, [], 'dropout'),
}

model = MNISTChebyshevGCNN(
    placeholders=placeholders,
    learning_rate=FLAGS.learning_rate,
    train_dir=FLAGS.train_dir,
    logging=True)


def preprocess_features(features):
    features = np.reshape(features, (features.shape[0], features.shape[1], 1))
    return perm_batch_of_features(features, model.perm)


def evaluate(features, labels):
    feed_dict = {
        placeholders['features']: features,
        placeholders['labels']: labels,
        placeholders['dropout']: 0.0,
    }

    loss, acc = sess.run([model.loss, model.accuracy], feed_dict)
    return loss, acc


sess = tf.Session()
global_step = model.initialize(sess)
writer = tf.summary.FileWriter(FLAGS.log_dir, sess.graph)

for step in xrange(global_step, FLAGS.max_steps):
    train_features, train_labels = mnist.train.next_batch(FLAGS.batch_size)
    train_features = preprocess_features(train_features)

    train_feed_dict = {
        placeholders['features']: train_features,
        placeholders['labels']: train_labels,
        placeholders['dropout']: FLAGS.dropout,
    }

    _, summary = sess.run([model.train, model.summary], train_feed_dict)
    writer.add_summary(summary, step)

    if step % FLAGS.display_step == 0:
        # Evaluate on training and validation set.
        train_loss, train_acc = evaluate(train_features, train_labels)

        val_features, val_labels = mnist.validation.next_batch(
            FLAGS.batch_size)
        val_features = preprocess_features(val_features)
        val_loss, val_acc = evaluate(val_features, val_labels)

        # Print results.
        print(', '.join([
            'Step: {}'.format(step),
            'train_loss={:.5f}'.format(train_loss),
            'train_acc={:.5f}'.format(train_acc),
            'val_loss={:.5f}'.format(val_loss),
            'val_acc={:.5f}'.format(val_acc),
        ]))

    if step % FLAGS.save_step == 0:
        model.save(sess)

print('Optimization finished!')

# Evaluate on test set.
test_features = mnist.test.images[:FLAGS.batch_size]
test_features = preprocess_features(test_features)
test_labels = mnist.test.labels[:FLAGS.batch_size]
test_loss, test_acc = evaluate(test_features, test_labels)
print('Test set results: cost={:.5f}, accuracy={:.5f}'.format(test_loss,
                                                              test_acc))
