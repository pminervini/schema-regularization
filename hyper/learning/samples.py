# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

import numpy as np


class IndexGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, n_samples, indices):
        pass


class UniformRandomIndexGenerator(IndexGenerator):
    """
    Instances of this class are used for generating random entity and predicate indices
    from an uniform distribution.
    """
    def __init__(self, random_state):
        """
        Initializes the generator.
        :param random_state: numpy.random.RandomState instance.
        """
        self.random_state = random_state

    def generate(self, n_samples, indices):
        """
        Creates a NumPy vector of 'n_samples', randomly selected by 'indices'.
        :param n_samples: Number of samples to generate.
        :param indices: List or NumPy vector containing the candidate indices.
        :return:
        """
        if isinstance(indices, list):
            indices = np.array(indices)

        rand_ints = self.random_state.random_integers(0, indices.size - 1, n_samples)
        return indices[rand_ints]


class GlorotRandomIndexGenerator(IndexGenerator):
    """
    Instances of this class are used for generating random entity and predicate indices
    using the method adopted in the code attached to the following paper:

    A Bordes et al. - Translating Embeddings for Modeling Multi-relational Data - NIPS 2013
    """
    def __init__(self, random_state):
        """
        Initializes the generator.
        :param random_state: numpy.random.RandomState instance.
        """
        self.random_state = random_state

    def generate(self, n_samples, indices):
        """
        Creates a NumPy vector of 'n_samples', randomly selected by 'indices'.
        :param n_samples: Number of samples to generate.
        :param indices: List or NumPy vector containing the candidate indices.
        :return:
        """
        if isinstance(indices, list):
            indices = np.array(indices)

        shuffled_indices = indices[self.random_state.permutation(len(indices))]
        rand_ints = shuffled_indices[np.arange(n_samples) % len(shuffled_indices)]
        return rand_ints