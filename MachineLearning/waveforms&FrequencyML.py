# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
import sklearn.model_selection as sk
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import getData
import time
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
import os

MODEL_NAME = "Frequency-{}".format(int(time.time()))
tensorboard = TensorBoard(log_dir=f'logs\\{MODEL_NAME}')

frameCount = 1000
timeFrame = "500"
numEpochs = 250

inputData,outputData = getData.getMachineLearningDataWaveforms(frameCount)
print(inputData.shape)

trainInput, testInput, trainOutput, testOutput = sk.train_test_split(inputData,outputData,test_size=0.1, random_state = 42)
input_1 =Input(shape=(frameCount, 3,))

waveformModel = keras.layers.AveragePooling1D(pool_size=3, strides=None, padding='valid', data_format='channels_last')(input_1)
waveformModel = keras.layers.GRU(100, activation='tanh', recurrent_activation='sigmoid', use_bias=True, kernel_initializer='glorot_uniform', recurrent_initializer='orthogonal', bias_initializer='zeros', kernel_regularizer=None, recurrent_regularizer=None, bias_regularizer=None, activity_regularizer=None, kernel_constraint=None, recurrent_constraint=None, bias_constraint=None, dropout=0.0, recurrent_dropout=0.0, implementation=2, return_sequences=False, return_state=False, go_backwards=False, stateful=False, unroll=False, reset_after=False)(waveformModel)
waveformModel = keras.layers.Flatten()(waveformModel)
waveformModel = keras.layers.Dense(650, activation=tf.nn.relu)(waveformModel)
waveformModel = keras.layers.GaussianDropout(0.01)(waveformModel)
waveformModel = keras.layers.Dense(450, activation=tf.nn.relu)(waveformModel)
waveformModel = keras.layers.Dense(200, activation=tf.nn.relu)(waveformModel)
output_wave = keras.layers.Dense(5, activation=tf.nn.softmax)(waveformModel)

frequencyModel = keras.layers.AveragePooling1D(pool_size=5,input_shape=(200, 3), strides=None, padding='valid', data_format='channels_last')(input_1)
frequencyModel =keras.layers.GRU(75, activation='tanh', recurrent_activation='sigmoid', use_bias=True, kernel_initializer='glorot_uniform', recurrent_initializer='orthogonal', bias_initializer='zeros', kernel_regularizer=None, recurrent_regularizer=None, bias_regularizer=None, activity_regularizer=None, kernel_constraint=None, recurrent_constraint=None, bias_constraint=None, dropout=0.0, recurrent_dropout=0.0, implementation=2, return_sequences=False, return_state=False, go_backwards=False, stateful=False, unroll=False, reset_after=False)(frequencyModel)
frequencyModel =keras.layers.Flatten()(frequencyModel)
frequencyModel =keras.layers.Dense(300, activation=tf.nn.sigmoid)(frequencyModel)
frequencyModel =keras.layers.GaussianDropout(0.01)(frequencyModel)
frequencyModel =keras.layers.Dense(150, activation=tf.nn.sigmoid)(frequencyModel)
frequencyModel =keras.layers.GaussianDropout(0.01)(frequencyModel)
frequencyModel =keras.layers.Dense(75, activation=tf.nn.sigmoid)(frequencyModel)
output_freq =keras.layers.Dense(4, activation=tf.nn.sigmoid)(frequencyModel)

model2 = Model(inputs = input_1,outputs = [output_wave,output_freq])


model2.compile(optimizer=tf.optimizers.Adamax(lr=0.001), 
              loss='sparse_categorical_crossentropy',# outputs multiple values, use binary_crossentropy for 1 or 0 output
              metrics=['accuracy'])
history = model2.fit(trainInput, trainOutput, validation_data=(testInput, testOutput),epochs=numEpochs,callbacks=[tensorboard]) #fit is same as train; epochs- how long to train, if you train too much you overfit the data
# if acc is a lot better than test accuracy then the data is overfit

#i added validation_data to get val_acc and val_loss in the history for the graphs

test_loss, test_acc = model2.evaluate(testInput, testOutput)

print('Test accuracy:', test_acc)

history_dict = history.history
history_dict.keys()
print(history_dict.keys())
#plot loss per training cycle, they should be close
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(1, len(acc) + 1)

np.save(os.path.join('MachineLearning','resultDataMotion', 'epochs.npy'),epochs)
np.save(os.path.join('MachineLearning','resultDataMotion',timeFrame +'loss.npy'),loss)
np.save(os.path.join('MachineLearning','resultDataMotion',timeFrame +'val_loss.npy'),val_loss)
np.save(os.path.join('MachineLearning','resultDataMotion',timeFrame +'acc.npy'),acc)
np.save(os.path.join('MachineLearning','resultDataMotion',timeFrame +'val_acc.npy'),val_acc)

# "bo" is for "blue dot"
plt.plot(epochs, loss, 'r', label='Training loss')
# b is for "solid blue line"
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

plt.plot(epochs, acc,'r', label='Training Accuracy')
plt.plot(epochs, val_acc,'b', label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()