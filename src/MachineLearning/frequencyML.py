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

frameSize = 200
timeFrame = "750"
inputData, outputData = getData.getMachineLearningData(frameSize, "frequency")
print(inputData.shape)

trainInput, testInput, trainOutput, testOutput = sk.train_test_split(
    inputData, outputData, test_size=0.1, random_state=42
)

model = keras.Sequential(
    [
        keras.layers.AveragePooling1D(
            pool_size=5, input_shape=(200, 3), strides=None, padding="valid", data_format="channels_last"
        ),
        keras.layers.GRU(
            75,
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
        keras.layers.Dense(300, activation=tf.nn.sigmoid),
        keras.layers.GaussianDropout(0.01),
        keras.layers.Dense(150, activation=tf.nn.sigmoid),
        keras.layers.GaussianDropout(0.01),
        keras.layers.Dense(75, activation=tf.nn.sigmoid),
        keras.layers.Dense(27, activation=tf.nn.sigmoid),
    ]
)

model.compile(
    optimizer=tf.optimizers.Adamax(),
    loss="sparse_categorical_crossentropy",  # outputs multiple values, use binary_crossentropy for 1 or 0 output
    metrics=["accuracy"],
)
history = model.fit(
    trainInput, trainOutput, validation_data=(testInput, testOutput), epochs=40, callbacks=[tensorboard]
)  # fit is same as train; epochs- how long to train, if you train too much you overfit the data

test_loss, test_acc = model.evaluate(testInput, testOutput)

print("Test accuracy:", test_acc)

history_dict = history.history

# plot loss per training cycle, they should be close
acc = history.history["accuracy"]
val_acc = history.history["val_accuracy"]
loss = history.history["loss"]
val_loss = history.history["val_loss"]

epochs = range(1, len(acc) + 1)

np.save(os.path.join("MachineLearning", "resultData", "epochs.npy"), epochs)
np.save(os.path.join("MachineLearning", "resultData", timeFrame + "loss.npy"), loss)
np.save(os.path.join("MachineLearning", "resultData", timeFrame + "val_loss.npy"), val_loss)
np.save(os.path.join("MachineLearning", "resultData", timeFrame + "acc.npy"), acc)
np.save(os.path.join("MachineLearning", "resultData", timeFrame + "val_acc.npy"), val_acc)

# "bo" is for "blue dot"
plt.plot(epochs, loss, "bo", label="Training loss")
# b is for "solid blue line"
plt.plot(epochs, val_loss, "b", label="Validation loss")
plt.title("Training and validation loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.show()

plt.plot(epochs, acc, "bo", label="Training Accuracy")
plt.plot(epochs, val_acc, "b", label="Validation Accuracy")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.show()
