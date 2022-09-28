import tensorflow as tf
from tensorflow import keras
import getData
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
import saveWaveformsAndFreqResult


def trainAndSave(model, frame_count, num_epochs, learning_rate):

    # (
    #     waveformTrainOutput,
    #     frequencyTrainOutput,
    #     waveformTestOutput,
    #     frequencyTestOutput,
    #     trainInput,
    #     testInput,
    # ) = getData.getMachineLearningDataWaveformsAndFrequency(frameCount)

    # Object test
    wf_data = getData.WaveAndFreqData(frame_count, "waveformsAndFrequency")

    model.compile(
        optimizer=tf.optimizers.Adamax(lr=learning_rate),
        loss="sparse_categorical_crossentropy",  # outputs multiple values, use binary_crossentropy for 1 or 0 output
        metrics=["accuracy"],
    )

    # Fit is same as train; epochs- how long to train, if you train too much you overfit the data
    # If acc is a lot better than test accuracy then the data is overfit
    history = model.fit(
        wf_data.train_input,
        [wf_data.waveform_train_output, wf_data.frequency_train_output],
        validation_data=(wf_data.test_input, [wf_data.waveform_test_output, wf_data.frequency_test_output]),
        epochs=num_epochs,
    )

    # i added validation_data to get val_acc and val_loss in the history for the graphs
    saveWaveformsAndFreqResult.save(
        history,
        model,
        wf_data.test_input,
        wf_data.waveform_test_output,
        wf_data.frequency_test_output,
        frame_count,
        num_epochs,
        learning_rate,
        False,
    )


if __name__ == "__main__":
    frameCount = 1000
    input_1 = Input(
        shape=(
            frameCount,
            3,
        ),
        name="Input",
    )

    common = keras.layers.AveragePooling1D(
        pool_size=3, strides=None, padding="valid", data_format="channels_last", name="Common_Pooling"
    )(input_1)
    common = keras.layers.GRU(
        180,
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
        name="Common_GRU",
    )(common)
    commmon = keras.layers.Flatten(name="Common_Flatten")(common)

    waveformModel = keras.layers.Dense(650, activation=tf.nn.relu, name="Waveform_Dense1")(commmon)
    waveformModel = keras.layers.GaussianDropout(0.01, name="Waveform_Dropout1")(waveformModel)
    waveformModel = keras.layers.Dense(550, activation=tf.nn.relu, name="Waveform_Dense2")(waveformModel)
    waveformModel = keras.layers.Dense(200, activation=tf.nn.relu, name="Waveform_Dense3")(waveformModel)
    output_wave = keras.layers.Dense(5, activation=tf.nn.softmax, name="Waveform")(waveformModel)

    frequencyModel = keras.layers.Dense(300, activation=tf.nn.sigmoid, name="Frequency_Dense1")(commmon)
    frequencyModel = keras.layers.GaussianDropout(0.01, name="Frequency_Dropout1")(frequencyModel)
    frequencyModel = keras.layers.Dense(150, activation=tf.nn.sigmoid, name="Frequency_Dense2")(frequencyModel)
    frequencyModel = keras.layers.GaussianDropout(0.01, name="Frequency_Dropout2")(frequencyModel)
    frequencyModel = keras.layers.Dense(75, activation=tf.nn.sigmoid, name="Frequency_Dense3")(frequencyModel)
    output_freq = keras.layers.Dense(4, activation=tf.nn.sigmoid, name="Frequency")(frequencyModel)
    model2 = Model(inputs=input_1, outputs=[output_wave, output_freq])

    trainAndSave(model2, frameCount, 500, 0.001)
