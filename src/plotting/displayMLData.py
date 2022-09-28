import os
import numpy as np
import matplotlib.pyplot as plt


epochs = np.load(os.path.join("MachineLearning", "resultData", "epochs.npy"))

loss750 = np.load(os.path.join("MachineLearning", "resultData", "750" + "loss.npy"))
val_loss750 = np.load(os.path.join("MachineLearning", "resultData", "750" + "val_loss.npy"))
acc750 = np.load(os.path.join("MachineLearning", "resultData", "750" + "acc.npy"))
val_acc750 = np.load(os.path.join("MachineLearning", "resultData", "750" + "val_acc.npy"))


loss1500 = np.load(os.path.join("MachineLearning", "resultData", "1500" + "loss.npy"))
val_loss1500 = np.load(os.path.join("MachineLearning", "resultData", "1500" + "val_loss.npy"))
acc1500 = np.load(os.path.join("MachineLearning", "resultData", "1500" + "acc.npy"))
val_acc1500 = np.load(os.path.join("MachineLearning", "resultData", "1500" + "val_acc.npy"))


plt.plot(epochs, loss750, "bo", label="Training loss 750us")
plt.plot(epochs, val_loss750, "b", label="Validation loss 750us")

plt.plot(epochs, loss1500, "ro", label="Training loss 1500us")
plt.plot(epochs, val_loss1500, "r", label="Validation loss 1500us")

plt.title("Training and validation loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.show()

plt.plot(epochs, acc750, "bo", label="Training Accuracy 750us")
plt.plot(epochs, val_acc750, "b", label="Validation Accuracy 750us")

plt.plot(epochs, acc1500, "ro", label="Training Accuracy 1500us")
plt.plot(epochs, val_acc1500, "r", label="Validation Accuracy 1500us")

plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.show()
