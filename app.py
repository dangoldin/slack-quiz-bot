#! /usr/bin/env python

import os
import random
import json

from sheet_helper import GSheetHelper
from slack_helper import SlackHelper

from flask import Flask
app = Flask(__name__)

gs = GSheetHelper(os.environ['CREDENTIALS_FILE'])
sh = SlackHelper(os.environ['SLACK_TOKEN'])

def get_questions():
    return gs.get_rows('Quiz questions', 'Questions')

@app.route('/quizme')
def quizme():
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

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
