import numpy as np
import operator
np.random.seed(1337)

import tweepy
from tweepy import OAuthHandler
 
#Twitter API credentials
consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

#returns text of all tweets of a given user in a list
def read_tweets(user):
    tweets = []
    new_tweets = api.user_timeline(screen_name = user, count=199, tweet_mode = "extended")
    tweets.extend(new_tweets)
    oldest = tweets[-1].id - 1
    while len(new_tweets) > 0:
        new_tweets = api.user_timeline(screen_name = user,count=199,max_id=oldest, tweet_mode = "extended")
        tweets.extend(new_tweets)
        oldest = tweets[-1].id - 1
    return [t.full_text for t in tweets]

#removes "RT", mentions, and twitter links 
def clean_tweets(tweet_list):
    new_lst = []
    for t in tweet_list:
        new_tweet = ""
        for word in t.split():
            if word != "RT" and word[0] != "@" and "https://t.co/" not in word:
                new_tweet += word + " "
        if new_tweet:
            new_lst.append(new_tweet)
    return new_lst

#creates a dictionary of words to unique integers starting at 3, where a lower number indicates a more frequent word
def get_word_dictionary(tweet_lst):
    all_words = []
    for lst in tweet_lst:
        for tweet in lst:
            for word in tweet.split():
                all_words.append(word)
    word_dict = {i:all_words.count(i) for i in set(all_words)}
    new_dict = {}
    i = 3
    for word in reversed(sorted(word_dict.items(), key=operator.itemgetter(1))):
        new_dict[word[0]] = i
        i += 1
    return new_dict

#takes in a list of tweets and a word frequency dictionary and returns encoded tweets, where
#1 indicates the start of a tweet, 2 indicates a word that isn't in the dictionary, and 3+ is the number of the word in the dictionary
def encode_tweets(tweet_lst, word_dict):
    all_tweets = []
    for lst in tweet_lst:
        file_tweets = []
        for tweet in lst:
            curr_tweet = [1]
            for word in tweet.split():
                if word not in word_dict:
                    curr_tweet.append(2)
                else:
                    curr_tweet.append(word_dict[word])
            file_tweets.append(curr_tweet)
        all_tweets.append(file_tweets)
    return all_tweets

#input a list of strings of usernames and their encoded names will be saved as a npy file
def save_files(user_lst):
	tweet_lst = []
	for user in user_lst:
		print("Now reading: " + user + "'s tweets")
		tweet_lst.append(clean_tweets(read_tweets(user)))
	word_dict = get_word_dictionary(tweet_lst)
	encoded = encode_tweets(tweet_lst, word_dict)
	for i in range(len(encoded)):
		np.save(user_lst[i] + "_tweets.npy", encoded[i])
		print("Saved " + user_lst[i] +"'s tweets" as user_lst[i] + "_tweets.npy")



