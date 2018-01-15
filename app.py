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

app = Flask(__name__)

questions_answers = {}
user_scores = defaultdict(lambda: [0, 0])

gs = GSheetHelper(os.environ['CREDENTIALS_FILE'])
sh = SlackHelper(os.environ['SLACK_TOKEN'])

def get_questions():
    return gs.get_rows('Quiz questions', 'Questions')

@app.route('/quizme', methods=['POST', 'GET'])
def quizme():
    app.logger.info('Got quizme request')

    # TODO: Use these later
    # user_id = request.form.get('user_id')
    # user_name = request.form.get('user_name')
    # text = request.form.get('text')

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
            'value': choice
        })

    return jsonify({
        "text": question_text,
        "attachments": [
            {
                # "text": question_text,
                "fallback": "Please answer the question",
                "callback_id": question_text,
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": actions
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

    user_scores[user_name][1] += 1 # Guesses
    if actual_answer == guess:
        user_scores[user_name][0] += 1 # Answers
        text = 'Correct'
    else:
        text = 'Wrong. Better luck next time. The answer was: ' + actual_answer

    text += '\nYou got ' + str(user_scores[user_name][0]) + ' out of ' + str(user_scores[user_name][1]) + ' correct'

    return jsonify({
        'text': text
    })

@app.route('/')
def index():
    questions = get_questions()
    return json.dumps(questions)

# From https://gist.github.com/sysradium/83118249d7930ef7dfbf
@app.before_first_request
def setup_logging():
    # if not app.debug:
    if True:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
