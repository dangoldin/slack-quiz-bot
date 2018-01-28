#! /usr/bin/env python

import os
import random
import json
import logging

from collections import defaultdict

from sheet_helper import GSheetHelper
from slack_helper import SlackHelper

from flask import Flask
from flask import request
from flask import jsonify
from flask import abort

from models import UserScore

app = Flask(__name__)

questions_answers = {}
user_scores = defaultdict(UserScore)

gs = GSheetHelper(os.environ['CREDENTIALS_FILE'])
sh = SlackHelper(os.environ['SLACK_TOKEN'])

def get_questions():
    return gs.get_rows('Quiz questions', 'Questions')

def get_message_info(request):
    return {
        'user_id': request.form.get('user_id'),
        'user_name': request.form.get('user_name'),
        'text': request.form.get('text'),
    }

@app.route('/quizme', methods=['POST', 'GET'])
def quizme():
    app.logger.info('Got quizme request')

    questions = get_questions()
    question = random.choice(questions)
    question_text = question['Question']
    choices = [question[x] for x in ('Answer', 'Choice A', 'Choice B', 'Choice C')]
    random.shuffle(choices)

    questions_answers[question_text] = question['Answer']

    app.logger.info('Question: %s, Answers: %s', question_text, choices)

    actions = []
    for choice in choices:
        actions.append({
            'name': 'responses',
            'text': choice,
            'type': 'button',
            'value': choice,
        })

    return jsonify({
        "text": question_text,
        "attachments": [
            {
                "fallback": "Please answer the question",
                "callback_id": question_text,
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": actions,
            }
        ]
    })

@app.route('/quizresponse', methods=['POST', 'GET'])
def quizresponse():
    app.logger.info('Quiz response %s', request.form)

    payload = json.loads(request.form.get('payload'))

    app.logger.info('Quiz response payload %s', payload)

    user_name = payload['user']['name']

    callback_question = payload['callback_id']
    guess = payload['actions'][0]['value']
    actual_answer = questions_answers[callback_question]

    app.logger.info('User scores: %s', user_scores[user_name])

    if actual_answer == guess:
        user_name[user_name].right()
        text = 'Correct'
    else:
        user_name[user_name].wrong()
        text = 'Wrong. Better luck next time. The answer was: ' + actual_answer

    text += 'You ' + user_scores[user_name].get_user_score_message()

    return jsonify({
        'text': text
    })

@app.route('/showstats', methods=['POST', 'GET'])
def showstats():
    message_info = get_message_info(request)
    user_name = message_info['user_name']

    app.logger.info('Showing stats for %s', user_name)

    if user_name in user_scores:
        text = 'You ' + user_scores[user_name].get_user_score_message()
    else:
        text = 'No scores found for ' + user_name

    return jsonify({
        'text': text,
    })

@app.route('/showallstats', methods=['POST', 'GET'])
def showallstats():
    return jsonify({
        'text': '\n'.join(user_name + ' ' + user_score.get_user_score_message() \
            for user_name, user_score in user_scores.iteritems())
    })

@app.route('/')
def index():
    abort(404)

# From https://gist.github.com/sysradium/83118249d7930ef7dfbf
@app.before_first_request
def setup_logging():
    app.logger.addHandler(logging.StreamHandler())
    if not app.debug:
        # TODO: In production mode, add log handler to sys.stderr.
        app.logger.setLevel(logging.INFO)
    else:
        app.logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
