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
numEpochs = 1

inputData,outputData = getData.getMachineLearningDataWaveformsAndFrequency(frameCount)
print(inputData.shape)

trainInput, testInput, trainOutput, testOutput = sk.train_test_split(inputData,outputData,test_size=0.1, random_state = 42)

waveformTrainOutput = []
frequencyTrainOutput = []
waveformTestOutput = []
frequencyTestOutput = []
for item in trainOutput:
    waveformTrainOutput.append(item[0])
    frequencyTrainOutput.append(item[1])

for item in testOutput:
    waveformTestOutput.append(item[0])
    frequencyTestOutput.append(item[1])


input_1 =Input(shape=(frameCount, 3,))

waveformModel = keras.layers.AveragePooling1D(pool_size=3, strides=None, padding='valid', data_format='channels_last')(input_1)
waveformModel = keras.layers.GRU(100, activation='tanh', recurrent_activation='sigmoid', use_bias=True, kernel_initializer='glorot_uniform', recurrent_initializer='orthogonal', bias_initializer='zeros', kernel_regularizer=None, recurrent_regularizer=None, bias_regularizer=None, activity_regularizer=None, kernel_constraint=None, recurrent_constraint=None, bias_constraint=None, dropout=0.0, recurrent_dropout=0.0, implementation=2, return_sequences=False, return_state=False, go_backwards=False, stateful=False, unroll=False, reset_after=False)(waveformModel)
waveformModel = keras.layers.Flatten()(waveformModel)
waveformModel = keras.layers.Dense(650, activation=tf.nn.relu)(waveformModel)
waveformModel = keras.layers.GaussianDropout(0.01)(waveformModel)
waveformModel = keras.layers.Dense(450, activation=tf.nn.relu)(waveformModel)
waveformModel = keras.layers.Dense(200, activation=tf.nn.relu)(waveformModel)
output_wave = keras.layers.Dense(5, activation=tf.nn.softmax, name="Waveform")(waveformModel)

frequencyModel = keras.layers.AveragePooling1D(pool_size=5,input_shape=(200, 3), strides=None, padding='valid', data_format='channels_last')(input_1)
frequencyModel = keras.layers.GRU(75, activation='tanh', recurrent_activation='sigmoid', use_bias=True, kernel_initializer='glorot_uniform', recurrent_initializer='orthogonal', bias_initializer='zeros', kernel_regularizer=None, recurrent_regularizer=None, bias_regularizer=None, activity_regularizer=None, kernel_constraint=None, recurrent_constraint=None, bias_constraint=None, dropout=0.0, recurrent_dropout=0.0, implementation=2, return_sequences=False, return_state=False, go_backwards=False, stateful=False, unroll=False, reset_after=False)(frequencyModel)
frequencyModel = keras.layers.Flatten()(frequencyModel)
frequencyModel = keras.layers.Dense(300, activation=tf.nn.sigmoid)(frequencyModel)
frequencyModel = keras.layers.GaussianDropout(0.01)(frequencyModel)
frequencyModel = keras.layers.Dense(150, activation=tf.nn.sigmoid)(frequencyModel)
frequencyModel = keras.layers.GaussianDropout(0.01)(frequencyModel)
frequencyModel = keras.layers.Dense(75, activation=tf.nn.sigmoid)(frequencyModel)
output_freq = keras.layers.Dense(4, activation=tf.nn.sigmoid, name="Frequency")(frequencyModel)

model2 = Model(inputs = input_1,outputs = [output_wave,output_freq])


model2.compile(optimizer=tf.optimizers.Adamax(lr=0.001), 
              loss='sparse_categorical_crossentropy',# outputs multiple values, use binary_crossentropy for 1 or 0 output
              metrics=['accuracy'])
history = model2.fit(trainInput, [np.array(waveformTrainOutput), np.array(frequencyTrainOutput)], validation_data=(testInput, [np.array(waveformTestOutput), np.array(frequencyTestOutput)]),epochs=numEpochs,callbacks=[tensorboard]) #fit is same as train; epochs- how long to train, if you train too much you overfit the data
# if acc is a lot better than test accuracy then the data is overfit

#i added validation_data to get val_acc and val_loss in the history for the graphs

test_loss, waveform_loss, frequency_loss, waveform_accuracy, frequency_accuracy = model2.evaluate(testInput, [np.array(waveformTestOutput),np.array(frequencyTestOutput)])

print('Waveform accuracy:', waveform_accuracy)
print('Frequency accuracy:', frequency_accuracy)

model2.summary()

history_dict = history.history
history_dict.keys()
print(history_dict.keys())

#plot loss per training cycle, they should be close
total_loss_v = history_dict['loss']
total_val_loss_v = history_dict['val_loss']
waveform_accuracy_v = history_dict['Waveform_accuracy']
frequency_accuracy_v = history_dict['Frequency_accuracy']
waveform_val_accuracy_v = history_dict['val_Waveform_accuracy']
frequency_val_accuracy_v = history_dict['val_Frequency_accuracy']

epochs = range(1, len(total_loss_v) + 1)


if not os.path.exists(os.path.join("results")):
    os.makedirs(os.path.join("results"))

if not os.path.exists(os.path.join("results","MachineLearning")):
    os.makedirs(os.path.join("results","MachineLearning"))

if not os.path.exists(os.path.join("results","MachineLearning","WaveformAndFreq")):
    os.makedirs(os.path.join("results","MachineLearning","WaveformAndFreq"))


nn_label = '_waveforms_and_freq'
nn_desc = "test"

if not os.path.exists(os.path.join("results","MachineLearning","WaveformAndFreq",nn_desc)):
    os.makedirs(os.path.join("results","MachineLearning","WaveformAndFreq",nn_desc))

resultPath =os.path.join("results","MachineLearning","WaveformAndFreq",nn_desc)
np.save(os.path.join(resultPath, 'epochs' + nn_label + '.npy'),epochs)
np.save(os.path.join(resultPath,timeFrame +'loss' + nn_label + '.npy'),total_loss_v)
np.save(os.path.join(resultPath,timeFrame +'val_loss' + nn_label + '.npy'),total_val_loss_v)
np.save(os.path.join(resultPath,timeFrame +'waveform_accuracy' + nn_label + '.npy'),waveform_accuracy_v)
np.save(os.path.join(resultPath,timeFrame +'frequency_accuracy' + nn_label + '.npy'),frequency_accuracy_v)
np.save(os.path.join(resultPath,timeFrame +'waveform_val_accuracy' + nn_label + '.npy'),waveform_val_accuracy_v)
np.save(os.path.join(resultPath,timeFrame +'frequency_val_accuracy' + nn_label + '.npy'),frequency_val_accuracy_v)

plt.title('Training and validation loss')
# "bo" is for "blue dot"
plt.plot(epochs, total_loss_v, 'r', label='Training loss')
# b is for "solid blue line"
plt.plot(epochs, total_val_loss_v, 'b', label='Validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.savefig(os.path.join(resultPath, "Loss.png"))
plt.show()


plt.plot(epochs, frequency_accuracy_v,'r', label='Frequency Accuracy')
plt.plot(epochs, frequency_val_accuracy_v,'g', label='Frequency Validation Accuracy')
plt.plot(epochs, waveform_val_accuracy_v,'b', label='Waveform Validation Accuracy')
plt.plot(epochs, waveform_val_accuracy_v,'y', label='Waveform Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.savefig(os.path.join(resultPath,"Accuracy.png"))
plt.show()
