# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
import sklearn.model_selection as sk
import numpy as np
import matplotlib.pyplot as plt
import getData
import time
from tensorflow.keras.callbacks import TensorBoard
import os

MODEL_NAME = f"Frequency-{int(time.time())}"
tensorboard = TensorBoard(log_dir=f"logs\\{MODEL_NAME}")

frameCount = 1000
timeFrame = "500"
num_epochs = 250

inputData, outputData = getData.getMachineLearningData(frameCount, "waveforms")
print(f"Input Shape: {inputData.shape}")

trainInput, testInput, trainOutput, testOutput = sk.train_test_split(
    inputData, outputData, test_size=0.1, random_state=42
)

model = keras.Sequential(
    [
        keras.layers.AveragePooling1D(
            pool_size=3, input_shape=(frameCount, 3), strides=None, padding="valid", data_format="channels_last"
        ),
        keras.layers.GRU(
            100,
            activation="tanh",
            recurrent_activation="sigmoid",
            use_bias=True,
            kernel_initializer="glorot_uniform",
            recurrent_initializer="orthogonal",
            bias_initializer="zeros",
            kernel_regularizer=None,
            recurrent_regularizer=None,
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            recurrent_constraint=None,
            bias_constraint=None,
            dropout=0.0,
            recurrent_dropout=0.0,
            implementation=2,
            return_sequences=False,
            return_state=False,
            go_backwards=False,
            stateful=False,
            unroll=False,
            reset_after=False,
        ),
        keras.layers.Flatten(),
        keras.layers.Dense(650, activation=tf.nn.relu),
        keras.layers.GaussianDropout(0.01),
        keras.layers.Dense(450, activation=tf.nn.relu),
        keras.layers.Dense(200, activation=tf.nn.relu),
        keras.layers.Dense(5, activation=tf.nn.softmax),
    ]
)

model.compile(
    optimizer=tf.optimizers.Adamax(lr=0.001),
    loss="sparse_categorical_crossentropy",  # outputs multiple values, use binary_crossentropy for 1 or 0 output
    metrics=["accuracy"],
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

np.save(os.path.join("MachineLearning", "resultDataMotion", "epochs.npy"), num_epochs)
np.save(os.path.join("MachineLearning", "resultDataMotion", timeFrame + "loss.npy"), loss)
np.save(os.path.join("MachineLearning", "resultDataMotion", timeFrame + "val_loss.npy"), val_loss)
np.save(os.path.join("MachineLearning", "resultDataMotion", timeFrame + "acc.npy"), acc)
np.save(os.path.join("MachineLearning", "resultDataMotion", timeFrame + "val_acc.npy"), val_acc)

plt.plot(num_epochs, loss, "r", label="Training loss")
plt.plot(num_epochs, val_loss, "b", label="Validation loss")
plt.title("Training and validation loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.show()

plt.plot(num_epochs, acc, "r", label="Training Accuracy")
plt.plot(num_epochs, val_acc, "b", label="Validation Accuracy")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.show()
