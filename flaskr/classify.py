from flask import Flask, Blueprint, send_from_directory, jsonify, render_template, request, redirect, url_for, g, flash
import numpy as np
from flaskr.cache import cache

from flaskr.miner import encode_tweets
from flaskr.classifier import trained_model, word_dict, build_model

from keras.models import model_from_json
from keras.preprocessing.text import Tokenizer
from keras import backend as K



bp = Blueprint('classify', __name__, url_prefix='/classify')

@bp.route('/', methods=('GET', 'POST'))
def index():
	if request.method == 'POST':
		one = request.form['first']
		two = request.form['second']
		return redirect(url_for("classify.get_result", user1=one, user2=two))
	return render_template('classify/index.html')

def process_text(model, text, dictionary):
	K.clear_session()
	tokenizer = Tokenizer(num_words=5000)
	text = encode_tweets([[text]], dictionary)
	text = tokenizer.sequences_to_matrix(text[0], mode='binary')
	return str(model.predict(text))

@bp.route('/<user1>/<user2>', methods=('GET', 'POST'))
@bp.route('/<user1>/<user2>/<user3>', methods=('GET', 'POST'))
@bp.route('/<user1>/<user2>/<user3>/<user4>', methods=('GET', 'POST'))
def get_result(user1, user2, user3=None, user4=None):
	if request.method == 'POST':
		K.clear_session()
		users = [user1, user2, user3, user4]
		text = request.form['text']
		model_weights = get_model_weights(user1, user2, user3, user4)
		model = model_from_json(model_layers(user1, user2, user3, user4))
		model.set_weights(model_weights)
		tokenizer = Tokenizer(num_words=5000)
		text = encode_tweets([[text]], get_dictionary(user1, user2, user3, user4))
		text = tokenizer.sequences_to_matrix(text[0], mode='binary')
		result = model.predict(text)[0]
		p_res = users[np.argmax(result)]
		confidence = max(result)
		return render_template('classify/result.html', res=p_res, conf=confidence)
	return render_template('classify/inputresult.html')

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




