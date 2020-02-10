import tensorflow as tf
from tensorflow import keras
import sklearn.model_selection as sk
import numpy as np
import getData
import time
import datetime
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
import os
import saveWaveformsAndFreqResult


def trainAndSave(model, frameCount, numEpochs):

    waveformTrainOutput, frequencyTrainOutput, waveformTestOutput, frequencyTestOutput, trainInput, testInput = getData.getMachineLearningDataWaveformsAndFrequency(frameCount)

    model.compile(optimizer=tf.optimizers.Adamax(lr=0.001), 
                loss='sparse_categorical_crossentropy',# outputs multiple values, use binary_crossentropy for 1 or 0 output
                metrics=['accuracy'])
    history = model.fit(trainInput, [waveformTrainOutput, frequencyTrainOutput], validation_data=(testInput, [waveformTestOutput,frequencyTestOutput]),epochs=numEpochs) #fit is same as train; epochs- how long to train, if you train too much you overfit the data
    # if acc is a lot better than test accuracy then the data is overfit

    #i added validation_data to get val_acc and val_loss in the history for the graphs
    saveWaveformsAndFreqResult.save(history,model, testInput, waveformTestOutput, frequencyTestOutput, frameCount,numEpochs, False )



if __name__ == "__main__":


    frameCount = 1000
    input_1 =Input(shape=(frameCount, 3,), name='Input')

    waveformModel = keras.layers.AveragePooling1D(pool_size=3, strides=None, padding='valid', data_format='channels_last', name='Waveform_Pooling')(input_1)
    waveformModel = keras.layers.GRU(180, activation='tanh', recurrent_activation='sigmoid', use_bias=True, kernel_initializer='glorot_uniform', recurrent_initializer='orthogonal', bias_initializer='zeros', kernel_regularizer=None, recurrent_regularizer=None, bias_regularizer=None, activity_regularizer=None, kernel_constraint=None, recurrent_constraint=None, bias_constraint=None, dropout=0.0, recurrent_dropout=0.0, implementation=2, return_sequences=False, return_state=False, go_backwards=False, stateful=False, unroll=False, reset_after=False, name='Waveform_GRU')(waveformModel)
    waveformModel = keras.layers.Flatten(name='Waveform_Flatten')(waveformModel)
    waveformModel = keras.layers.Dense(650, activation=tf.nn.relu, name='Waveform_Dense1')(waveformModel)
    waveformModel = keras.layers.GaussianDropout(0.01, name='Waveform_Dropout1')(waveformModel)
    waveformModel = keras.layers.Dense(550, activation=tf.nn.relu, name='Waveform_Dense2')(waveformModel)
    waveformModel = keras.layers.Dense(200, activation=tf.nn.relu, name='Waveform_Dense3')(waveformModel)
    output_wave = keras.layers.Dense(5, activation=tf.nn.softmax, name="Waveform")(waveformModel)

    frequencyModel = keras.layers.AveragePooling1D(pool_size=5, strides=None, padding='valid', data_format='channels_last', name='Frequency_Pooling')(input_1)
    frequencyModel = keras.layers.GRU(60, activation='tanh', recurrent_activation='sigmoid', use_bias=True, kernel_initializer='glorot_uniform', recurrent_initializer='orthogonal', bias_initializer='zeros', kernel_regularizer=None, recurrent_regularizer=None, bias_regularizer=None, activity_regularizer=None, kernel_constraint=None, recurrent_constraint=None, bias_constraint=None, dropout=0.0, recurrent_dropout=0.0, implementation=2, return_sequences=False, return_state=False, go_backwards=False, stateful=False, unroll=False, reset_after=False, name='Frequency_GRU')(frequencyModel)
    frequencyModel = keras.layers.Flatten(name='Frequency_Flatten')(frequencyModel)
    frequencyModel = keras.layers.Dense(300, activation=tf.nn.sigmoid, name='Frequency_Dense1')(frequencyModel)
    frequencyModel = keras.layers.GaussianDropout(0.01, name='Frequency_Dropout1')(frequencyModel)
    frequencyModel = keras.layers.Dense(150, activation=tf.nn.sigmoid, name='Frequency_Dense2')(frequencyModel)
    frequencyModel = keras.layers.GaussianDropout(0.01, name='Frequency_Dropout2')(frequencyModel)
    frequencyModel = keras.layers.Dense(75, activation=tf.nn.sigmoid, name='Frequency_Dense3')(frequencyModel)
    output_freq = keras.layers.Dense(4, activation=tf.nn.sigmoid, name="Frequency")(frequencyModel)
    model2 = Model(inputs = input_1,outputs = [output_wave,output_freq])

    trainAndSave(model2, frameCount, 500)