# -*- coding: utf-8 -*-

import codecs
import pandas as pd
import numpy as np


def calculate_transformation_matrix(model_source, model_target, training_dict):
    # model_source and model_target are both preloaded fasttext models
    # training_dict is a csv (comma separated!), with headers source and target
    word_pairs = codecs.open(training_dict, 'r', 'utf-8')
    pairs = pd.read_csv(word_pairs)
    pairs['vector_source'] = [model_source[pairs['source'][n]] for n in range(len(pairs))]
    pairs['vector_target'] = [model_target[pairs['target'][n]] for n in range(len(pairs))]
    matrix_train_source = pd.DataFrame(pairs['vector_source'].tolist()).values
    matrix_train_target = pd.DataFrame(pairs['vector_target'].tolist()).values
    print('Generating translation matrix')
    # Matrix W is given in  http://stackoverflow.com/questions/27980159/fit-a-linear-transformation-in-python
    translation_matrix = np.linalg.pinv(matrix_train_source).dot(matrix_train_target).T
    print(translation_matrix.shape)
    print('Generated translation matrix')
    return translation_matrix
