#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 12:00:25 2019

@author: xudachengthu

define the method of forward propagation

/Users/xudachengthu/Downloads/GHdataset/ftraining-0.h5 --the file downloaded from crowdAI

uisng the .tfrecords file generated by generate.py
"""

import tensorflow as tf

INPUT_NODE = 400
OUTPUT_NODE = 400
LAYER1_NODE = 800
LAYER2_NODE = 800

def get_weight(shape, regularizer):
    w = tf.Variable(tf.truncated_normal(shape,stddev=0.1))
    if regularizer != None:
        tf.add_to_collection('losses', tf.contrib.layers.l2_regularizer(regularizer)(w))
    return w

def get_bias(shape):
    b = tf.Variable(tf.zeros(shape))
    return b

def forwardpro(x, regularizer):
    w1 = get_weight([INPUT_NODE, LAYER1_NODE], regularizer)
    b1 = get_bias([LAYER1_NODE])
    #y1 = tf.nn.relu(tf.matmul(x, w1) + b1)
    y1 = tf.nn.sigmoid(tf.matmul(x, w1) + b1)

    w2 = get_weight([LAYER1_NODE, LAYER2_NODE], regularizer)
    b2 = get_bias([LAYER2_NODE])
    #y2 = tf.nn.relu(tf.matmul(y1, w2) + b2)
    y2 = tf.nn.sigmoid(tf.matmul(y1, w2) + b2)
    
    w3 = get_weight([LAYER2_NODE, OUTPUT_NODE], regularizer)
    b3 = get_bias([OUTPUT_NODE])
    y = tf.matmul(y2, w3) + b3
    
    return y
