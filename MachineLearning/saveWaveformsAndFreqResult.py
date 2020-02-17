import numpy as np
import os
import time
import datetime
import matplotlib
import matplotlib.pyplot as plt
def save(history,model, testInput, waveformTestOutput, frequencyTestOutput, frameCount,numEpochs, show_plots ):
    test_loss, waveform_loss, frequency_loss, waveform_accuracy, frequency_accuracy = model.evaluate(testInput, [waveformTestOutput, frequencyTestOutput])

    print('Waveform accuracy:', waveform_accuracy)
    print('Frequency accuracy:', frequency_accuracy)

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
    nn_desc = datetime.datetime.now().strftime("%b-%d-%Y-%H-%M-%S")
    resultPath = os.path.join("results","MachineLearning","WaveformAndFreq", nn_desc)

    if not os.path.exists(os.path.join("results","MachineLearning","WaveformAndFreq",nn_desc)):
        os.makedirs(os.path.join("results","MachineLearning","WaveformAndFreq",nn_desc))

    # Write NN result data to file
    with open(os.path.join(resultPath, 'results.txt'), 'w') as f:
        model.summary(print_fn=lambda x: f.write(x + '\n'))
        f.write('\n')
        f.write(f'Frame Count: {frameCount}\n')
        f.write(f'Num Epochs: {numEpochs}\n')
        f.write(f'Total Loss: {total_loss_v[-1]}\n')
        f.write(f'Total Validation Loss: {test_loss}\n')
        f.write(f'Waveform Accuracy: {waveform_accuracy_v[-1]}\n')
        f.write(f'Waveform Validation Accuracy: {waveform_accuracy}\n')
        f.write(f'Frequency Accuracy: {frequency_accuracy_v[-1]}\n')
        f.write(f'Frequency Validaion Accuracy: {frequency_accuracy}\n')

    np.save(os.path.join(resultPath, 'epochs' + nn_label + '.npy'),epochs)
    np.save(os.path.join(resultPath, 'loss' + nn_label + '.npy'),total_loss_v)
    np.save(os.path.join(resultPath, 'val_loss' + nn_label + '.npy'),total_val_loss_v)
    np.save(os.path.join(resultPath, 'waveform_accuracy' + nn_label + '.npy'),waveform_accuracy_v)
    np.save(os.path.join(resultPath, 'frequency_accuracy' + nn_label + '.npy'),frequency_accuracy_v)
    np.save(os.path.join(resultPath, 'waveform_val_accuracy' + nn_label + '.npy'),waveform_val_accuracy_v)
    np.save(os.path.join(resultPath, 'frequency_val_accuracy' + nn_label + '.npy'),frequency_val_accuracy_v)

    plt.title('Training and validation loss')
    # "bo" is for "blue dot"
    plt.plot(epochs, total_loss_v, 'r', label='Training loss')
    # b is for "solid blue line"
    plt.plot(epochs, total_val_loss_v, 'b', label='Validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(os.path.join(resultPath, "Loss.png"))

    if show_plots:
        plt.show()
    else:
        plt.clf()

    plt.plot(epochs, frequency_accuracy_v,'r', label='Frequency Accuracy')
    plt.plot(epochs, frequency_val_accuracy_v,'g', label='Frequency Validation Accuracy')
    plt.plot(epochs, waveform_val_accuracy_v,'b', label='Waveform Validation Accuracy')
    plt.plot(epochs, waveform_accuracy_v,'y', label='Waveform Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig(os.path.join(resultPath,"Accuracy.png"))

    if show_plots:
        plt.show()
    else:
        plt.clf()