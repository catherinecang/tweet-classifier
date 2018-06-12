from flask import Flask, Blueprint, send_from_directory, render_template, request, redirect, url_for, g
from flaskr.cache import cache
from flaskr.miner import get_word_dictionary, clean_tweets, read_tweets

import operator

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

@bp.route('/', methods=['GET', 'POST'])
def index():
	options = ['Word Frequency']
	if request.method == 'POST':
		user = request.form['user']
		if request.form.get('options') == 'Word Frequency':
			return redirect(url_for("analyze.freq", user=user))
	return render_template('analyze/index.html', options=options)

@bp.route('/frequency/<user>', methods=['GET', 'POST'])
def freq(user):
	options = ['Word Frequency']
	if request.method == 'POST':
		tweet_lst = read_tweets(user)
		top_lst=[]
		start = int(request.form['start'])
		end = int(request.form['end'])
		word_counts = get_word_counts(clean_tweets(tweet_lst))
		i = 1
		for word in reversed(sorted(word_counts.items(), key=operator.itemgetter(1))):
			top_lst.append(str(i) + ". " + str(word[0]))
			i += 1
		return render_template('analyze/word_freq.html', options=options, lst=top_lst[max(start-1, 0):min(end, len(top_lst))], user=user)
	return render_template('analyze/word_freq.html', options=options, lst=["Waiting to be analyzed"], user=user)
		
			
	#mentions = get_word_counts(common_mentions(tweet_lst))
	

@cache.memoize(timeout=0)
def common_mentions(tweet_lst):
	mentions = []
	for t in tweet_lst:
		for word in t.split():
			if word[0] == '@':
				if not word[len(word) - 1].isalnum():
					word = word[:len(word) - 1]
				mentions.append(word.lower())
	return mentions

@cache.memoize(timeout=0)
def get_word_counts(tweet_lst):
	all_words = []
	for tweet in tweet_lst:
		for word in tweet.split():
			all_words.append(word.lower())
	return {i:all_words.count(i) for i in set(all_words)}
