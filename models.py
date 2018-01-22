#! /usr/bin/env python

class UserScore:
    def __init__(self):
        self.num_questions = 0
        self.num_right = 0

    def right(self):
        self.num_questions += 1
        self.num_right += 1

    def wrong(self):
        self.num_questions += 1

    def get_user_score_message(self):
        return 'got ' + str(self.num_right) + ' out of ' + str(self.num_questions) + ' correct'
