# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
import sklearn.model_selection as sk



# Helper libraries

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import getData
frameSize = 25
inputData,outputData = getData.getMachineLearningData(frameSize)
print(inputData.shape)

trainInput, testInput, trainOutput, testOutput = sk.train_test_split(inputData,outputData,test_size=0.1, random_state = 42)


model = keras.Sequential([
    keras.layers.Flatten(input_shape=(frameSize, 3)),
    keras.layers.Dense(900, activation=tf.nn.sigmoid),#number of nodes always use relu
    keras.layers.Dense(900, activation=tf.nn.sigmoid),#number of nodes always use relu
    keras.layers.Dense(27, activation=tf.nn.sigmoid)#number of classes(for pictures), softmax is a % of possible outputs,
                                                    # output putting one dense layer will give a number from +- infinite
                                                    # outputting 1 sigmoid will give one percentage 
])



model.compile(optimizer=tf.optimizers.Adam(), 
              loss='sparse_categorical_crossentropy',# outputs multiple values, use binary_crossentropy for 1 or 0 output
              metrics=['accuracy'])
history = model.fit(trainInput, trainOutput, validation_data=(testInput, testOutput),epochs=200) #fit is same as train; epochs- how long to train, if you train too much you overfit the data
# if acc is a lot better than test accuracy then the data is overfit

#i added validation_data to get val_acc and val_loss in the history for the graphs

test_loss, test_acc = model.evaluate(testInput, testOutput)

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

# "bo" is for "blue dot"
plt.plot(epochs, loss, 'bo', label='Training loss')
# b is for "solid blue line"
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.savefig("pythonPlot2.png")
plt.show()


