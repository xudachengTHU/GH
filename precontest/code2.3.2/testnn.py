#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 12:01:00 2019

@author: xudachengthu

define the method of test

/Users/xudachengthu/Downloads/GHdataset/ftraining-0.h5 --the file downloaded from crowdAI

uisng the .tfrecords file generated by generate.py
"""

import time
import tensorflow as tf
import numpy as np
import forward
import backward
import generate

TEST_INTERVAL_SECS = 10
TEST_NUM = 500
REG_RAW = [84.28899, 0]
REG = np.array(REG_RAW)

def test():
    with tf.Graph().as_default():
        x = tf.placeholder(tf.float32, [TEST_NUM, 1, generate.Length_waveform, forward.NUM_CHANNELS])
        #y_ = tf.placeholder(tf.float32, [None, forward.OUTPUT_NODE])
        y = forward.forwardpro(x, False, None)
        
        ema = tf.train.ExponentialMovingAverage(backward.MOVING_AVERAGE_DECAY)
        ema_restore = ema.variables_to_restore()
        saver = tf.train.Saver(ema_restore)
        
        #saver = tf.train.Saver()
        
        wf_batch, pet_batch, aver_batch = generate.get_tfrecord(TEST_NUM, isTrain=False)
        '''
        y_predict = tf.add(tf.div(tf.sign(tf.subtract(y,0.5)),2),0.5)
        correct_prediction = tf.equal(y_, y_predict)
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        '''
        while True:
            with tf.Session() as sess:
                ckpt = tf.train.get_checkpoint_state(backward.MODEL_SAVE_PATH)
                if ckpt and ckpt.model_checkpoint_path:
                    saver.restore(sess, ckpt.model_checkpoint_path)
                    global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                    
                    coord = tf.train.Coordinator()
                    threads = tf.train.start_queue_runners(sess=sess, coord=coord)
                    
                    xs, ys, vs= sess.run([wf_batch, pet_batch,aver_batch])
                    reshaped_xs = np.reshape(xs,(TEST_NUM, 1, 
                                             generate.Length_waveform, 
                                             forward.NUM_CHANNELS))
                    
                    y_value = sess.run(y, feed_dict={x: reshaped_xs})
                    
                    pe_num = np.around(np.polyval(REG, vs))
                    y_predict = np.zeros_like(y_value)
                    for i in range(TEST_NUM):
                        order_y = np.argsort(y_value[i, :])[::-1]
                        th_v = y_value[i, :][int(order_y[int(np.round((pe_num[i])))])]
                        y_predict[i, :] = np.where(y_value[i,:] > th_v, 1, 0)
                        
                        #correction of bias
                        if np.size(np.where(y_predict[i, :])) != 0:
                            a = np.where(y_predict[i, :] == 1)[0][0]
                            b = np.where(y_predict[i, :] == 1)[0][-1]
                            p = int(np.around((2.*b - 3.*a)/5))
                            y_predict[i, p::] = 0
                    
                    accuracy_score = np.divide(np.sum(np.multiply(ys, y_predict)), np.sum(ys))
                    precision = np.divide(np.sum(np.multiply(ys, y_predict)), np.sum(y_predict))
                    recall = np.divide(np.sum(np.multiply(ys, y_predict)), np.sum(ys))
                    '''
                    y_predict_value = sess.run(y_predict, feed_dict={x: reshaped_xs, y_: ys})
                    accuracy_score = sess.run(accuracy, feed_dict={y_: ys, y_predict: y_predict_value})
                    precision = np.divide(np.sum(np.multiply(ys, y_predict_value)), np.sum(y_predict_value))
                    recall = np.divide(np.sum(np.multiply(ys, y_predict_value)), np.sum(ys))
                    '''
                    print("After %s training step(s), test accuracy = %g" % (global_step, accuracy_score))
                    print("After %s training step(s), test precision = %g" % (global_step, precision))
                    print("After %s training step(s), test recall = %g" % (global_step, recall))
                    
                    coord.request_stop()
                    coord.join(threads)
                else:
                    print("No checkpoint found")
                    return time.sleep(TEST_INTERVAL_SECS)

def main():
    test()

if __name__ == '__main__':
    main()