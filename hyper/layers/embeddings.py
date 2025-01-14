# -*- coding: utf-8 -*-

import theano
import theano.tensor as T

from keras import backend as K
from keras import initializations, regularizers, constraints
from keras.engine import Layer

import logging


class Frame:
    def __init__(self, row_start, row_end, col_start, col_end):
        # Item indices considered by the frame
        self.row_start, self.row_end = row_start, row_end

        # Start and end of the embedding vectors
        self.col_start, self.col_end = col_start, col_end

    def __str__(self):
        return str((self.row_start, self.row_end, self.col_start, self.col_end))

    def __repr__(self):
        return "<Frame %s at %x>" % (str((self.row_start, self.row_end, self.col_start, self.col_end)), id(self))


class FrameEmbedding(Layer):
    input_ndim = 2

    def __init__(self, input_dim, output_dim, frames=None,
                 init='uniform', input_length=None,
                 W_regularizer=None, activity_regularizer=None,
                 W_constraint=None,
                 mask_zero=False,
                 weights=None,
                 **kwargs):

        self.input_dim = input_dim
        self.output_dim = output_dim
        self.frames = frames

        self.frame_parameters = []
        self.W = None

        self.init = initializations.get(init)
        self.input_length = input_length
        self.mask_zero = mask_zero

        self.W_constraint = constraints.get(W_constraint)

        self.W_regularizer = regularizers.get(W_regularizer)
        self.activity_regularizer = regularizers.get(activity_regularizer)

        self.initial_weights = weights
        kwargs['input_shape'] = (self.input_length,)
        kwargs['input_dtype'] = 'int32'

        super(FrameEmbedding, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = K.zeros(shape=(self.input_dim, self.output_dim))

        self.frame_parameters = []
        for frame in self.frames:
            logging.info('Adding frame %s ..' % repr(frame))

            frame_input_dim = frame.row_end - frame.row_start
            frame_output_dim = frame.col_end - frame.col_start

            W_frame = self.init((frame_input_dim, frame_output_dim), name='{}_W'.format(self.name))
            self.frame_parameters.append(W_frame)

            self.W = T.set_subtensor(self.W[frame.row_start:frame.row_end, frame.col_start:frame.col_end], W_frame)

        self.trainable_weights = self.frame_parameters

        self.constraints = {}
        if self.W_constraint:
            for W_frame in self.frame_parameters:
                self.constraints[W_frame] = self.W_constraint

        self.regularizers = []
        if self.W_regularizer:
            self.W_regularizer.set_param(self.W)
            self.regularizers.append(self.W_regularizer)

        if self.activity_regularizer:
            self.activity_regularizer.set_layer(self)
            self.regularizers.append(self.activity_regularizer)

        if self.initial_weights is not None:
            self.set_weights(self.initial_weights)

    def compute_mask(self, x, mask=None):
        if not self.mask_zero:
            return None
        else:
            return K.not_equal(x, 0)

    def get_output_shape_for(self, input_shape):
        if not self.input_length:
            input_length = input_shape[1]
        else:
            input_length = self.input_length
        return input_shape[0], input_length, self.output_dim

    def call(self, x, mask=None):
        W = self.W
        out = K.gather(W, x)
        return out

    def get_config(self):
        config = {'input_dim': self.input_dim, 'output_dim': self.output_dim,
                  'init': self.init.__name__, 'input_length': self.input_length, 'mask_zero': self.mask_zero,
                  'activity_regularizer': self.activity_regularizer.get_config() if self.activity_regularizer else None,
                  'W_regularizer': self.W_regularizer.get_config() if self.W_regularizer else None,
                  'W_constraint': self.W_constraint.get_config() if self.W_constraint else None}
        base_config = super(FrameEmbedding, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class LowRankEmbedding(Layer):
    input_ndim = 2

    def __init__(self, input_dim, output_dim, rank=None,
                 init='uniform', input_length=None,
                 W_regularizer=None, activity_regularizer=None,
                 W_constraint=None,
                 mask_zero=False,
                 weights=None,
                 **kwargs):

        self.input_dim = input_dim
        self.output_dim = output_dim
        self.rank = rank

        self.L, self.R = None, None
        self.W = None

        self.init = initializations.get(init)
        self.input_length = input_length
        self.mask_zero = mask_zero

        self.W_constraint = constraints.get(W_constraint)

        self.W_regularizer = regularizers.get(W_regularizer)
        self.activity_regularizer = regularizers.get(activity_regularizer)

        self.initial_weights = weights
        kwargs['input_shape'] = (self.input_length,)
        kwargs['input_dtype'] = 'int32'

        super(LowRankEmbedding, self).__init__(**kwargs)

    def build(self, input_shape):
        self.L = self.init((self.input_dim, self.rank), name='{}_L'.format(self.name))
        self.R = self.init((self.output_dim, self.rank), name='{}_R'.format(self.name))

        self.W = K.dot(self.L, K.transpose(self.R))

        self.trainable_weights = [self.L, self.R]

        self.constraints = {}
        if self.W_constraint:
            for W_frame in self.trainable_weights:
                self.constraints[W_frame] = self.W_constraint

        self.regularizers = []
        if self.W_regularizer:
            self.W_regularizer.set_param(self.W)
            self.regularizers.append(self.W_regularizer)

        if self.activity_regularizer:
            self.activity_regularizer.set_layer(self)
            self.regularizers.append(self.activity_regularizer)

        if self.initial_weights is not None:
            self.set_weights(self.initial_weights)

    def compute_mask(self, x, mask=None):
        if not self.mask_zero:
            return None
        else:
            return K.not_equal(x, 0)

    def get_output_shape_for(self, input_shape):
        if not self.input_length:
            input_length = input_shape[1]
        else:
            input_length = self.input_length
        return input_shape[0], input_length, self.output_dim

    def call(self, x, mask=None):
        W = self.W
        out = K.gather(W, x)
        return out

    def get_config(self):
        config = {'input_dim': self.input_dim, 'output_dim': self.output_dim,
                  'init': self.init.__name__, 'input_length': self.input_length, 'mask_zero': self.mask_zero,
                  'activity_regularizer': self.activity_regularizer.get_config() if self.activity_regularizer else None,
                  'W_regularizer': self.W_regularizer.get_config() if self.W_regularizer else None,
                  'W_constraint': self.W_constraint.get_config() if self.W_constraint else None}
        base_config = super(LowRankEmbedding, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
