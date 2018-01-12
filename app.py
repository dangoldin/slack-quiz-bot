#! /usr/bin/env python

import os
import random
import json
import logging

from sheet_helper import GSheetHelper
from slack_helper import SlackHelper

from flask import Flask
from flask import request

app = Flask(__name__)

gs = GSheetHelper(os.environ['CREDENTIALS_FILE'])
sh = SlackHelper(os.environ['SLACK_TOKEN'])

def get_questions():
    return gs.get_rows('Quiz questions', 'Questions')

@app.route('/quizme', methods=['POST', 'GET'])
def quizme():
    app.logger.info('Request args: %s', request.args)

    questions = get_questions()
    question = random.choice(questions)
    answer = question['Answer']
    choices = [question[x] for x in ('Choice A', 'Choice B', 'Choice C')]
    return json.dumps({
        'question': question['Question'],
        'answer': answer,
        'choices': choices,
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
