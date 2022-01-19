from tensorflow.keras.layers import Dropout, Dense, Flatten, Activation, AvgPool2D
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
import os
import cv2
import pickle
import random
import argparse
import matplotlib.pyplot as plt
from imutils import paths
from tensorflow.keras.layers import Dense, MaxPooling2D, Conv2D
from tensorflow.keras.models import Sequential
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import VGG16
from sklearn.preprocessing import LabelBinarizer
from tensorflow.keras.optimizers import SGD
import numpy as np
import matplotlib
from airflow.models.xcom import XCom


def train(model,**kwargs):
    INIT_LR = 0.0001
    EPOCHS = int(args["epoch"])
    print("[INFO] тренерую")
    opt = SGD(lr=INIT_LR)

    model.compile(loss="categorical_crossentropy", optimizer=opt,
                  metrics=["accuracy"])

    H = model.fit(trainX, trainY, validation_data=(testX, testY),
                  epochs=EPOCHS, batch_size=32, verbose=2)
    predictions = model.predict(testX, batch_size=32)
    print(classification_report(testY.argmax(axis=1),
                                predictions.argmax(axis=1), target_names=lb.classes_))

    score = model.evaluate(testX, testY, verbose=0)
    print("Точность: %.2f%%" % (score[1]*100))
    try:
        N = np.arange(0, EPOCHS)
        plt.style.use("ggplot")
        plt.figure()
        plt.plot(N, H.history["loss"], label="train_loss")
        plt.plot(N, H.history["val_loss"], label="val_loss")
        plt.title("Loss and Accuracy")
        plt.xlabel("Эпохи")
        plt.ylabel("Loss/Accuracy")
        plt.legend()
        plt.savefig(args["plot"])
    except:
        pass

    print("[INFO] сохраняю")
    model.save_weights(args["model"]+"weights.h5")
    model.save(args["model"])
    f = open(args["label_bin"], "wb")
    f.write(pickle.dumps(lb))
    f.close()
    print((score[1]*100))








def build(tensor_shape):
    base_model = VGG16(weights='imagenet', include_top=False,
                       input_shape=tensor_shape)

    model = base_model.output

    model = AvgPool2D()(model)

    model = Dense(1024, activation='relu')(model)
    model = Dropout(0.5)(model)
    model = Flatten()(model)
    model = Dense(256, activation='relu')(model)
    model = Dropout(0.5)(model)

    predictions = (Dense(len(lb.classes_), activation="softmax"))(model)

    model_ok = Model(inputs=base_model.input, outputs=predictions)

    train( model_ok)


def build3(tensor_shape):
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3),
                     activation='relu', input_shape=tensor_shape))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(len(lb.classes_), activation="softmax"))
    train(model)


def build2(tensor_shape):
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3),
                     activation='relu', input_shape=tensor_shape))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(lb.classes_), activation='softmax'))
    train(model)


matplotlib.use("Agg")
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
                help="img")
ap.add_argument("-m", "--model", required=True,
                help="model")
ap.add_argument("-l", "--label-bin", required=True,
                help="label ")
ap.add_argument("-p", "--plot", required=True,
                help="picture")
ap.add_argument("-e", "--epoch", required=True,
                help="эпохи")


args = vars(ap.parse_args())

print("[INFO] Загружаю картинки")
data = []
labels = []


imagePaths = sorted(list(paths.list_images(args["dataset"])))
random.seed(200)
random.shuffle(imagePaths)
i = 0
for imagePath in imagePaths:
    try:

        print(imagePath)

        image = cv2.imread(imagePath)

        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_CUBIC)
        data.append(image)
        label = imagePath.split(os.path.sep)[-2]
        labels.append(label)

    except:

        print(len(labels))


data = np.array(data, dtype="float32")
labels = np.array(labels)
(trainX, testX, trainY, testY) = train_test_split(data,
                                                  labels, test_size=0.25, random_state=200)
lb = LabelBinarizer()
trainY = lb.fit_transform(trainY)
testY = lb.transform(testY)
tensor_shape = (224, 224, 3)
print("Выбор")
ar=str(args["model"])
if (ar == '/root/airflow/dags/1.h5'):
                build(tensor_shape)
if (ar == '/root/airflow/dags/2.h5'):
                build2(tensor_shape)
if (ar == '/root/airflow/dags/3.h5'):
                build3(tensor_shape)

