FROM python:3.6.1

# Do requirements first for docker caching
COPY requirements.txt /slack-quiz-bot/

# Download packages
RUN pip install -r /slack-quiz-bot/requirements.txt

COPY . /slack-quiz-bot

WORKDIR /slack-quiz-bot/

CMD ["python", "app.py"]
