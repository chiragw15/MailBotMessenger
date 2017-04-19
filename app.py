import os
import sys
import json
from watson_developer_cloud import ConversationV1

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
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
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    try:
                        message_text = messaging_event["message"]["text"]  # the message's text
                        message_text=(message_text.lower()).split()
                        log(message_text)                
                        if "hi" in message_text or "hello" in message_text or "hey" in message_text or "hii" in message_text or "yo" in message_text:
                        #if any(c in message_text.lower() for c in ("hello", "hey", "hii", "hi", "yo")):    
                            get_username(sender_id)   
                        else:
                            get_response_for_query(message_text,sender_id)
                        break
                    except KeyError:
                        send_message(sender_id,"Please stick to text only. Thanks!!")
                        pass

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def get_response_for_query(message_text,sender_id):
    conversation = ConversationV1(
        username='b053dacb-cb93-40a2-aee4-b3c2cedb751f',
        password='UrwZSyeVKtgV',
        version='2017-04-18'
    )

    # Replace with the context obtained from the initial request
    context = {}

    workspace_id = 'f125e325-585c-433c-b460-70d9dab9ec1a'

    response = conversation.message(
        workspace_id=workspace_id,
        message_input={'text': message_text},
        context=context
    )
    context = response["context"]
    send_message(sender_id,response["output"]["text"])

    log(json.dumps(response, indent=2))

def get_username(sender_id):

    url = "https://graph.facebook.com/v2.6/" + sender_id + "?" + "access_token=" + os.environ["PAGE_ACCESS_TOKEN"] 
    log(url)
    r = requests.get(url)
    log(r.status_code)
    data = r.json()
    log("hi " + data["first_name"]);
    send_message(sender_id, "hi " + data["first_name"]);


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
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


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
