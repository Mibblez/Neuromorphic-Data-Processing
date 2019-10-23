import tensorflow as tf
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D,Conv1D
import getData
frameSize = 25
X,y = getData.getMachineLearningData(frameSize)


test = X.shape[-1]
#X = X/255.0

model = Sequential()

model.add(Conv1D(1000, ( 3), input_shape=(frameSize, 3)))
model.add(Activation('sigmoid'))

model.add(Conv1D(1000, ( 3)))
model.add(Activation('sigmoid'))

model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors

model.add(Dense(64))

model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])


model.fit(X, y, batch_size=32, epochs=3, validation_split=0.3)