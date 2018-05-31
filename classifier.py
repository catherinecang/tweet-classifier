import numpy as np
from random import shuffle
np.random.seed(1337)

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.utils import np_utils
from keras.preprocessing.text import Tokenizer

import sys

#takes in a list of file addresses e.g. ["BarackObama_tweets.npy", "officialjaden_tweets.npy"]
#split indicates the train/test data split
#returns data split into X, y train/test values
def get_inputs(file_lst, split = 0.2):
    all_tweets = []
    i = 0
    for file in file_lst:
        f = np.load(file)
        for t in f:
            all_tweets.append((t, i))
        i += 1
    shuffle(all_tweets)
    X_train, y_train = [], []
    X_test, y_test = [], []
    split_num = int(len(all_tweets) * split)
    for i in range(split_num):
        X_test.append(all_tweets[i][0])
        y_test.append(all_tweets[i][1])
    for i in range(split_num, len(all_tweets)):
        X_train.append(all_tweets[i][0])
        y_train.append(all_tweets[i][1])
        #tokenize data
    tokenizer = Tokenizer(num_words=5000)
    X_train = tokenizer.sequences_to_matrix(X_train, mode='binary')
    X_test = tokenizer.sequences_to_matrix(X_test, mode='binary')
    Y_train = np_utils.to_categorical(y_train, num_categories)
    Y_test = np_utils.to_categorical(y_test, num_categories)
    return (X_train, Y_train), (X_test, Y_test)


def build_model(X_train, Y_train, X_test, Y_test, num_categories):
    #build model
    model = Sequential()
    model.add(Dense(512, input_shape=(5000,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(256, activation='linear'))
    model.add(Dropout(0.5))
    model.add(Dense(num_categories))
    model.add(Activation('sigmoid'))
    return model

#uses command line inputs. first input is the number of users as categories. the rest are each user file
#example CLI: python3 classifier.py 2 officialjaden.npy BarackObama.npy
if __name__ == '__main__':
    num_categories = int(sys.argv[1])
    file_lst = []
    for i in range(2, 2 + num_categories):
        file_lst.append(sys.argv[i])
    (X_train, Y_train), (X_test, Y_test) = get_inputs(file_lst)
    model = build_model(X_train, Y_train, X_test, Y_test, num_categories)

    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    model.fit(X_train, Y_train,
                    epochs=25, batch_size=32,
                    verbose=1, validation_split=0.1)
    score = model.evaluate(X_test, Y_test,
                       batch_size=32, verbose=1)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])

