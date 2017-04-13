import os
import sys
import json

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
                            send_message(sender_id,"What can I do for you today?")
                        elif "write" in message_text or "mail" in message_text or "yes" in message_text:    
                            send_message(sender_id,"We are working on writing mails!! It will be up soon");   
                        else:
                            send_message(sender_id,"Sorry, I didn't understand that. Should I write a mail?")
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
