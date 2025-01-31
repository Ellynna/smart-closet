import os
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras import Model, Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


def get_data(input_size=(299, 299)):
    base_dir = 'static/datasets'
    train_dir = os.path.join(base_dir, 'train')
    validation_dir = os.path.join(base_dir, 'validation')
    test_dir = os.path.join(base_dir, 'test')

    train_datagen = ImageDataGenerator(rescale=1./255.,
                                       rotation_range=40,
                                       width_shift_range=0.2,
                                       height_shift_range=0.2,
                                       shear_range=0.2,
                                       zoom_range=0.2,
                                       horizontal_flip=True)
    test_datagen = ImageDataGenerator(rescale=1./255.)

    train_generator = train_datagen.flow_from_directory(train_dir,
                                                        batch_size=20,
                                                        class_mode='categorical',
                                                        target_size=input_size)
    validation_generator = train_datagen.flow_from_directory(validation_dir,
                                                             batch_size=20,
                                                             class_mode='categorical',
                                                             target_size=input_size)
    test_generator = test_datagen.flow_from_directory(test_dir,
                                                      batch_size=20,
                                                      class_mode='categorical',
                                                      target_size=input_size)
    return train_generator, validation_generator, test_generator


# 한 epoch 당 45~60s
def basic_cnn_model():
    basic_cnn_model = Sequential()
    basic_cnn_model.add(Conv2D(32, (3,3), activation='relu', input_shape=(299, 299, 3)))
    basic_cnn_model.add(MaxPooling2D(2,2))
    basic_cnn_model.add(Conv2D(64, (3,3), activation='relu'))
    basic_cnn_model.add(MaxPooling2D(2,2))
    basic_cnn_model.add(Conv2D(64, (3,3), activation='relu'))
    basic_cnn_model.add(Flatten())
    basic_cnn_model.add(Dense(7, activation='softmax'))
    return basic_cnn_model


def inceptionV3_classifier():
    inceptionV3 = InceptionV3(include_top=True)
    base_inputs = inceptionV3.layers[0].input
    base_outputs = inceptionV3.layers[-2].output
    classifier = Dense(7, activation='softmax')(base_outputs)
    inceptionV3_model = Model(inputs=base_inputs, outputs=classifier)
    return inceptionV3_model


def inceptionV3_fine_tunning():
    inception_V3 = InceptionV3(weights='imagenet', input_shape=(299, 299, 3), include_top=True)
    for layer in inception_V3.layers[:]:
        layer.trainable = True
    base_inputs = inception_V3.layers[0].input
    base_outputs = inception_V3.layers[-2].output
    classifier = tf.keras.layers.Dense(7, activation='softmax')(base_outputs)
    inceptionV3_ft_model = tf.keras.Model(inputs=base_inputs, outputs=classifier)

    return inceptionV3_ft_model


def train_model(model, name, train_generator, validation_generator):
    model.compile(loss=CategoricalCrossentropy(),
                              optimizer=Adam(),
                              metrics=["accuracy"])

    early_stopping = EarlyStopping(monitor='val_loss', patience=17)

    checkpoint_path = 'static/checkpoints/'
    cb_checkpoint = ModelCheckpoint(os.path.join(checkpoint_path,
                                                 'c2c_{name}_model.ckpt'.format(name=name)),
                                    save_weights_only=True,
                                    monitor='val_loss',
                                    verbose=1,
                                    save_best_only=True)

    model_history = model.fit(train_generator,
                              validation_data=validation_generator,
                              epochs=100,
                              callbacks=[cb_checkpoint, early_stopping])

    model.save(os.path.join("models", "c2c_{name}_model.h5".format(name=name)))


if __name__ == '__main__':
    train, valid, test = get_data()
    cnn_model = basic_cnn_model()
    inceptionV3_clas = inceptionV3_classifier()
    inceptionV3_fine = inceptionV3_fine_tunning()
    train_model(cnn_model, "cnn", train, valid)
    train_model(inceptionV3_clas, "ic", train, valid)
    train_model(inceptionV3_fine, "ift", train, valid)


