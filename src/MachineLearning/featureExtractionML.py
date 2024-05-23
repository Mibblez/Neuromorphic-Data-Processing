# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
import sklearn.model_selection as sk
import numpy as np
import matplotlib.pyplot as plt
import get_data
import time
from tensorflow.keras.callbacks import TensorBoard
import os
from keras.layers import Dense, GRU, AveragePooling1D, Flatten
from keras.models import Sequential, Model
import pickle

MODEL_NAME = f"Background-{int(time.time())}"
tensorboard = TensorBoard(log_dir=f"logs\\{MODEL_NAME}")

frameCount = 1000
timeFrame = "500"
num_epochs = 2

inputData, outputData = get_data.getMachineLearningDataBackground(frameCount, "backgrounds")
print(f"Input Shape: {inputData.shape}")

trainInput, testInput, trainOutput, testOutput = sk.train_test_split(
    inputData, outputData, test_size=0.1, random_state=42
)

model = keras.Sequential(
    [
        keras.Input(shape=(frameCount, 3)),
        keras.layers.Dense(64, activation=tf.nn.relu),
        keras.layers.Dense(32, activation=tf.nn.relu),
        keras.layers.Dense(16, activation=tf.nn.relu, name="feature_layer"),
        keras.layers.Flatten(),
        keras.layers.Dense(5, activation=tf.nn.softmax),  # Number must be equal to number of classes+1
    ]
)

model.compile(
    optimizer=tf.optimizers.Adamax(learning_rate=0.001), loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

history = model.fit(
    trainInput, trainOutput, validation_data=(testInput, testOutput), epochs=num_epochs, callbacks=[tensorboard]
)  # fit is same as train; epochs- how long to train, if you train too much you overfit the data

test_loss, test_acc = model.evaluate(testInput, testOutput)

print(f"Test accuracy: {test_acc}")

history_dict = history.history

# plot loss per training cycle, they should be close
acc = history.history["accuracy"]
val_acc = history.history["val_accuracy"]
loss = history.history["loss"]
val_loss = history.history["val_loss"]

machine_learning_folder = "MachineLearning"
result_data_background = "resultDataBackground"

if not os.path.exists(machine_learning_folder):
    os.mkdir(machine_learning_folder)

if not os.path.exists(os.path.join(machine_learning_folder, result_data_background)):
    os.mkdir(os.path.join(machine_learning_folder, result_data_background))

epochs = range(1, len(acc) + 1)


features = keras.Model(
    inputs=model.inputs,
    outputs=model.get_layer(name="feature_layer").output,
)

with open("test.pkl", "wb") as file:
    pickle.dump(features.predict(trainInput), file)
