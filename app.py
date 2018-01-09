#! /usr/bin/env python

import os

from sheet_helper import GSheetHelper
from slack_helper import SlackHelper

from flask import Flask
app = Flask(__name__)

gs = GSheetHelper(os.environ['CREDENTIALS_FILE'])
sh = SlackHelper(os.environ['SLACK_TOKEN'])

@app.route('/')
def index():
    questions = gs.get_rows('Quiz questions', 'Questions')
    return str(questions)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
