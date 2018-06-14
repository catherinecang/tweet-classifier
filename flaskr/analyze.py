from flask import Flask, Blueprint, send_from_directory, render_template, request, redirect, url_for, g
from flaskr.cache import cache
from flaskr.miner import get_word_dictionary, clean_tweets, read_tweets

import operator
import string
import emoji

bp = Blueprint('analyze', __name__, url_prefix='/analyze')

options = ['Word Frequency', 'Mention Frequency', 'Hashtag Frequency', 'Emoji Frequency']
@bp.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		user = request.form['user']
		return redirect_analyze(user, request.form.get('options'))
	return render_template('analyze/index.html', options=options)

@bp.route('/words/<user>', methods=['GET', 'POST'])
def freq(user):
	if request.method == 'POST':
		if request.form['user'] != user or request.form.get('options') != options[0]:
			return redirect_analyze(request.form['user'], request.form.get('options'))
		tweet_lst = read_tweets(user)
		top_lst=[]
		word_counts = get_word_counts(clean_tweets(tweet_lst))
		i = 1
		for word in reversed(sorted(word_counts.items(), key=operator.itemgetter(1))):
			top_lst.append(str(i) + ". " + str(word[0]))
			i += 1
		start, end = request.form['start'], request.form['end']
		start, end = get_start_end(start, end, len(top_lst))
		return render_template('analyze/word_freq.html', options=options, lst=top_lst[max(start-1, 0):min(end, len(top_lst))], user=user)
	return render_template('analyze/word_freq.html', options=options, lst=["Waiting to be analyzed"], user=user)

@bp.route('/mentions/<user>', methods=['GET', 'POST'])
def mentions(user):
	if request.method == 'POST':
		if request.form['user'] != user or request.form.get('options') != options[1]:
			return redirect_analyze(request.form['user'], request.form.get('options'))
		top_lst = freq_helper(common_mentions, user)
		start, end = request.form['start'], request.form['end']
		start, end = get_start_end(start, end, len(top_lst))
		return render_template('analyze/mentions.html', options=options, lst=top_lst[max(start-1, 0):min(end, len(top_lst))], user=user)
	return render_template('analyze/mentions.html', options=options, lst=["Waiting to be analyzed"], user=user)

@bp.route('/hashtags/<user>', methods=['GET', 'POST'])
def hashtags(user):
	if request.method == 'POST':
		if request.form['user'] != user or request.form.get('options') != options[2]:
				return redirect_analyze(request.form['user'], request.form.get('options'))
		top_lst = freq_helper(common_hashtags, user)
		start, end = request.form['start'], request.form['end']
		start, end = get_start_end(start, end, len(top_lst))
		return render_template('analyze/hashtags.html', options=options, lst=top_lst[max(start-1, 0):min(end, len(top_lst))], user=user)
	return render_template('analyze/hashtags.html', options=options, lst=["Waiting to be analyzed"], user=user)

@bp.route('/emojis/<user>', methods=['GET', 'POST'])
def emojis(user):
	if request.method == 'POST':
		if request.form['user'] != user or request.form.get('options') != options[3]:
				return redirect_analyze(request.form['user'], request.form.get('options'))
		top_lst = freq_helper(common_emojis, user)
		start, end = request.form['start'], request.form['end']
		start, end = get_start_end(start, end, len(top_lst))
		return render_template('analyze/emojis.html', options=options, lst=top_lst[max(start-1, 0):min(end, len(top_lst))], user=user)
	return render_template('analyze/emojis.html', options=options, lst=["Waiting to be analyzed"], user=user)

def redirect_analyze(user, param):
	if param == 'Word Frequency':
		return redirect(url_for("analyze.freq", user=user))
	elif param == 'Mention Frequency':
		return redirect(url_for("analyze.mentions", user=user))
	elif param == 'Hashtag Frequency':
		return redirect(url_for("analyze.hashtags", user=user))
	elif param == 'Emoji Frequency':
		return redirect(url_for("analyze.emojis", user=user))

def get_start_end(start, end, max_len):
	try: 
		start = int(start)
	except ValueError:
		start = 0
	try: 
		end = int(end)
	except ValueError:
		end = max_len
	return start, end

def freq_helper(f, user):
	tweet_lst = read_tweets(user)
	top_lst=[]
	count_lst = get_word_counts(f(tweet_lst))
	i = 1
	for word in reversed(sorted(count_lst.items(), key=operator.itemgetter(1))):
		top_lst.append(str(i) + ". " + str(word[0]))
		i += 1
	return top_lst

@cache.memoize(timeout=0)
def common_mentions(tweet_lst):
	mentions = []
	for t in tweet_lst:
		if t.split()[0] != "RT":
			for word in t.split():
				if word[0] == '@':
					new_word = '@'
					for c in word[1:]:
						if c in set(string.punctuation + "—") and c != "_":
							break
						else:
							new_word += c
					mentions.append(new_word.lower())
	return mentions

def common_emojis(tweet_lst):
	emojis = []
	for t in tweet_lst:
		if t.split()[0] != "RT":
			for c in t:
				if c in emoji.UNICODE_EMOJI:
					emojis.append(c)
	return emojis

def common_hashtags(tweet_lst):
	hashtags = []
	for t in tweet_lst:
		if t.split()[0] != "RT":
			for word in t.split():
				if word[0] == '#':
					new_word = '#'
					for c in word[1:]:
						if c in set(string.punctuation + "—") and c != "_":
							break
						else:
							new_word += c
					hashtags.append(new_word.lower())
	return hashtags

@cache.memoize(timeout=0)
def get_word_counts(tweet_lst):
	all_words = []
	for tweet in tweet_lst:
		for word in tweet.split():
			all_words.append(word.lower())
	return {i:all_words.count(i) for i in set(all_words)}
