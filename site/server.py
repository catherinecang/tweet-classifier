from flask import Flask, send_from_directory, jsonify, render_template, request, redirect, url_for, g, flash
from flask_cache import Cache
import numpy as np

from miner import encode_tweets
from classifier import trained_model, word_dict, build_model

from keras.models import model_from_json
from keras.preprocessing.text import Tokenizer
from keras import backend as K 

app = Flask(__name__)
app.config.from_object(__name__)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

 
@app.route('/', methods=('GET', 'POST'))
def index():
	if request.method == 'POST':
		one = request.form['first']
		two = request.form['second']
		return redirect(url_for("get_result", user1=one, user2=two))
	return render_template('classify/index.html')
 
def process_text(model, text, dictionary):
	K.clear_session()
	tokenizer = Tokenizer(num_words=5000)
	text = encode_tweets([[text]], dictionary)
	text = tokenizer.sequences_to_matrix(text[0], mode='binary')
	return str(model.predict(text))

@app.route('/<user1>/<user2>', methods=('GET', 'POST'))
@app.route('/<user1>/<user2>/<user3>', methods=('GET', 'POST'))
@app.route('/<user1>/<user2>/<user3>/<user4>', methods=('GET', 'POST'))
def get_result(user1, user2, user3=None, user4=None):
	if request.method == 'POST':
		K.clear_session()
		text = request.form['text']
		model_weights = get_model_weights(user1, user2, user3, user4)
		model = model_from_json(model_layers(user1, user2, user3, user4))
		model.set_weights(model_weights)
		tokenizer = Tokenizer(num_words=5000)
		text = encode_tweets([[text]], get_dictionary(user1, user2, user3, user4))
		text = tokenizer.sequences_to_matrix(text[0], mode='binary')
		result = str(model.predict(text))
		return render_template('classify/result.html', res=result)
	return render_template('classify/result.html', res="This may take some time, sorry!")

@cache.memoize(timeout=86400)
def big_test():
	import time
	time.sleep(5)
	return [np.array([1,2,3])]

@cache.memoize(timeout=86400)
def get_dictionary(user1, user2, user3=None, user4=None):
	return word_dict(user1, user2, user3, user4)

def model_layers(user1, user2, user3=None, user4=None):
	user_lst = [user1, user2, user3, user4]
	user_len = len([user for user in user_lst if user is not None])
	return build_model(user_len).to_json()

@cache.memoize(timeout=86400)
def get_model_weights(user1, user2, user3=None, user4=None):
	model = trained_model(user1, user2, user3, user4)
	return model.get_weights()
