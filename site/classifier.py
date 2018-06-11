import numpy as np
from random import shuffle
np.random.seed(1337)

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.utils import np_utils
from keras.preprocessing.text import Tokenizer
from keras.models import model_from_json

from miner import read_tweets, clean_tweets, get_word_dictionary, encode_tweets

import os
import sys

#takes in a dictionary of names to encoded tweets
#split indicates the train/test data split
#returns data split into X, y train/test values
def get_inputs(tweet_dict, split = 0.2):
    all_tweets = []
    tweet_lst = list(tweet_dict.values())
    num_categories = len(tweet_dict)
    i = 0
    for tweet in tweet_lst:
        for t in tweet:
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


def build_model(num_categories):
    #build model
    model = Sequential()
    model.add(Dense(512, input_shape=(5000,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_categories))
    model.add(Activation('sigmoid'))
    return model

def word_dict(user1, user2, user3, user4):
    user_lst = [user1, user2, user3, user4]
    user_lst = [user for user in user_lst if user is not None]
    tweet_lst = []
    for user in user_lst:
        tweet_lst.append(clean_tweets(read_tweets(user)))
    return get_word_dictionary(tweet_lst)
    
def trained_model(user1, user2, user3=None, user4=None):
    user_lst = [user1, user2, user3, user4]
    user_lst = [user for user in user_lst if user is not None]
    num_categories = len(user_lst)
    tweet_lst = []
    for user in user_lst:
        print("currently working on: " + user)
        tweet_lst.append(clean_tweets(read_tweets(user)))
    word_dict = get_word_dictionary(tweet_lst)
    encoded = encode_tweets(tweet_lst, word_dict)
    user_dict = {} 
    for i in range(len(encoded)):
        user_dict[user_lst[i]] = encoded[i]
    (X_train, Y_train), (X_test, Y_test) = get_inputs(user_dict)
    model = build_model(num_categories)

    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    model.fit(X_train, Y_train,
                    epochs=20, batch_size=32,
                    verbose=1, validation_split=0.1)
    return model