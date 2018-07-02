import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from configs import REF_CODES,MIN_UPVOTES,URL_TYPES


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://hvwgndxuyeivyt:672d1adbf6758964915db3de14ce87cc36402e4a0da7f1a81cb367c1029d36cc@ec2-107-22-183-40.compute-1.amazonaws.com:5432/d7r9jp8ifvptuc"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


import models


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "lociloci":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    if models.User.query.filter_by(id_user=str(messaging_event["sender"]["id"])).count() > 0:
                        send_message(sender_id, "Wait for new promotions")
                    else:
                        send_message(sender_id, "Got it")
                        record = models.User()
                        record.id_user = str(messaging_event["sender"]["id"])
                        db.session.add(record)
                        db.session.commit()

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": "EAACEdEose0cBACFtqPZB3UXkeTznZCoQANlyVFg8myFFZB8BZBkYwlZAYjmsKNXiY1a5afKgYExODfe8dBsa0FZBSkD5USZCVWibBtEd7QZAihk9awQLJ6ZCC5EAh7x10ivIxNP1ULbnu9PbEs4yxZC32QhOQAZBVT09nQSFras1QfFpccvzA6ZCvE5PfofrQ2pxPGIZD"
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        print("{}: {}").format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
