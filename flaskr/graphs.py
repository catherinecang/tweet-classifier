from flask import Flask, Blueprint, send_from_directory, render_template, request, redirect, url_for, g
from flaskr.cache import cache

from matplotlib import pyplot as plt
from flaskr.miner import tweet_times, clean_with_mentions, read_tweets

import datetime
import mpld3 

bp = Blueprint('graphs', __name__, url_prefix='/graphs')

@bp.route('/', methods=['POST', 'GET'])
def index():
	if request.method == 'POST':
		user = request.form['user']
		return redirect("/graphs/"+user+"#times")
	return render_template("graphs/index.html")

@bp.route('/<user>', methods=['POST', 'GET'])
def user_graphs(user):
	og_hours = [t.hour for t in tweet_times(user)]
	hour_dict = {i:og_hours.count(i) for i in range(24)}
	time_html_graph = draw_graph(hour_dict, "Hour")
	len_dict = tweet_length_dictionary(user)
	len_html_graph = draw_graph(len_dict, "Length in Characters")
	year_dict = year_dictionary(user)
	year_html_graph= draw_graph(year_dict, "Year")
	if request.method == 'POST':
		print("Here's the form: " + str(request.form))
		if request.form['action'] == "Get Started":
			print('ya yeet')
			user = request.form['user']
			print(user)
			return redirect("/graphs/"+user)
		elif request.form['action'] == "Update Time Zone":
			offset = request.form.get("zones")
			hours = update_time_zone(offset, og_hours)
			hour_dict = {i:hours.count(i) for i in range(24)}
			time_html_graph = draw_graph(hour_dict, "Hours")
			return render_template("graphs/user_graphs.html",time_graph=[time_html_graph], sign = offset[0], s=int(offset[1:]), len_graph=[len_html_graph], year_graph=[year_html_graph])
	return render_template("graphs/user_graphs.html",time_graph=[time_html_graph], s = 0, sign='+', len_graph=[len_html_graph], year_graph=[year_html_graph])

def update_time_zone(offset, hours):
	num = int(offset[1:])
	if offset[0]=='-':
		hours = [(h - num) % 24 for h in hours]
	else:
		hours = [(h + num) % 24 for h in hours]
	return hours

@cache.memoize(timeout=86400)
def tweet_length_dictionary(user):
	lengths = []
	tweet_lst = clean_with_mentions(read_tweets(user))
	for t in tweet_lst:
		lengths.append(len(t))
	return {i:lengths.count(i) for i in range(1, 281)}

def year_dictionary(user):
	years = [t.year for t in tweet_times(user)]
	return {i:years.count(i) for i in range(2006, datetime.date.today().year + 1)}

def draw_graph(val_dict, x):
	fig, ax = plt.subplots()
	values = list(val_dict.values())
	boxes = ax.bar(list(val_dict.keys()), values)
	plt.xlabel(x)
	plt.ylabel("Number of Tweets")
	for i in range(len(values)):
		tooltip = mpld3.plugins.LineLabelTooltip(boxes[i], values[i])
		mpld3.plugins.connect(fig, tooltip)
	return mpld3.fig_to_html(fig)


#deprecated
@bp.route('time/<user>', methods=['GET', 'POST'])
def time_graph(user):
	hours = [t.hour for t in tweet_times(user)]
	hour_dict = {i:hours.count(i) for i in range(24)}
	html_graph = draw_graph(hour_dict, "Hour")
	if request.method == 'POST':
		offset = request.form.get("zones")
		num = int(offset[1:])
		if offset[0]=='-':
			hours = [(h - num) % 24 for h in hours]
		else:
			hours = [(h + num) % 24 for h in hours]
		hour_dict = {i:hours.count(i) for i in range(24)}
		html_graph = draw_graph(hour_dict, "Hour")
		return render_template('graphs/time.html', graph=[html_graph], sign=offset[0], s = num)
	return render_template('graphs/time.html', graph=[html_graph], s = 0)
