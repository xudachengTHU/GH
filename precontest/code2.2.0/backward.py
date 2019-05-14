#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 12:00:43 2019

@author: xudachengthu

define the method of backward propagation

/Users/xudachengthu/Downloads/GHdataset/ftraining-0.h5 --the file downloaded from crowdAI

uisng the .tfrecords file generated by generate.py
"""

import tensorflow as tf
import os
import forward
import generate

BATCH_SIZE = 200
LEARNING_RATE_BASE = 0.01
LEARNING_RATE_DECAY = 0.99
REGULARIZER = 0.000001
STEPS = 10
MOVING_AVERAGE_DECAY = 0.99
MODEL_SAVE_PATH = "/Users/xudachengthu/Downloads/GHdataset/model/"
MODEL_NAME = "findpe_model"
train_num_examples = 2000

def backwardpro():
    with tf.Graph().as_default():
        x = tf.placeholder(tf.float32, [None, forward.INPUT_NODE])
        y_ = tf.placeholder(tf.float32, [None, forward.OUTPUT_NODE])
        y = forward.forwardpro(x, REGULARIZER)
        global_step = tf.Variable(0, trainable=False)
        '''
        ce = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y, labels=tf.argmax(y_, 1))
        cem = tf.reduce_mean(ce)
        loss = cem + tf.add_n(tf.get_collection('losses'))
        '''
        loss = tf.reduce_mean(tf.square(y_ - y)) + tf.add_n(tf.get_collection('losses'))
        
        learning_rate = tf.train.exponential_decay(
                LEARNING_RATE_BASE,
                global_step,
                train_num_examples / BATCH_SIZE, 
                LEARNING_RATE_DECAY,
                staircase=True)
        train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step=global_step)
        
        ema = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)
        ema_op = ema.apply(tf.trainable_variables())
        with tf.control_dependencies([train_step, ema_op]):
            train_op = tf.no_op(name='train')
        
        saver = tf.train.Saver()
        wf_batch, pet_batch = generate.get_tfrecord(BATCH_SIZE, isTrain=True)
        
        with tf.Session() as sess:
            init_op = tf.global_variables_initializer()
            sess.run(init_op)
            
            ckpt = tf.train.get_checkpoint_state(MODEL_SAVE_PATH)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
            
            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(sess=sess, coord=coord)
            
            for i in range(STEPS):
                xs, ys = sess.run([wf_batch, pet_batch])
                _, loss_value, step = sess.run([train_op, loss, global_step], 
                                           feed_dict={x: xs, y_: ys})
                if i % 1 == 0:
                    print("After %d training step(s), loss on training batch is %g." % (step, loss_value))
                    saver.save(sess, os.path.join(MODEL_SAVE_PATH, MODEL_NAME), global_step=global_step)
            
            coord.request_stop()
            coord.join(threads)

def main():
    backwardpro()

if __name__ == '__main__':
    main()