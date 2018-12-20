import os
import flask
import requests
from flask_sqlalchemy import SQLAlchemy
from scrappyreddit import bot_loggin, get_memes_bot, random_url, get_thoughts_bot


FACEBOOK_API_MESSAGE_SEND_URL = "https://graph.facebook.com/v2.6/me/messages"

app = flask.Flask(__name__)

# TODO: Set environment variables appropriately.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    facebook_id = db.Column(db.String, unique=True)
    count_messages = db.Column(db.Integer, default=0)


def handle_message(message, sender_id):

    reddit = bot_loggin()
    list_urls_memes = get_memes_bot(reddit)
    list_urls_shower = get_thoughts_bot(reddit)

    user = User.query.filter(User.facebook_id == sender_id).first()

    if not user:
        user = User(facebook_id=sender_id)
        db.session.add(user)
        db.session.commit()
        return "Hi I'm the your pick-me-up bot.\n What is your name? "

    elif not user.username:
        user.username = message
        db.session.add(user)
        db.session.commit()
        return "Hi, %s! Are you having a bad day? Yes or No" % (user.username)

    elif "YES" in message or "yes" in message or "Yes" in message:
        number_memes = len(list_urls_memes)
        number_thoughts = len(list_urls_shower)
        return "I have %i memes and %i shower thoughts to cheer you up.\nType: 'meme' or 'shower' to see them" \
               % (number_memes, number_thoughts)

    # If an user wants a meme send one
    elif "SHOWER" in message or "shower" in message or "Shower" in message:
        shower_title = random_url(list_urls_shower)
        list_urls_shower.remove(shower_title)
        return shower_title

    elif "MEME" in message or "meme" in message or "Meme" in message:
        picture_url = random_url(list_urls_memes)
        list_urls_memes.remove(picture_url)
        payload = {'url': picture_url}
        return payload

    # If an user wants a shower thought send one

    elif "NO" in message or "no" in message or "not" in message or "No" in message or "Not" in message or "NOT" in message:
        return "That's the spirit %s! Have a good one!" % (user.username)

    return "I'm the Pick-me-up bot.\nAre you having a bad day? Yes or No"


@app.route('/', methods=['GET', 'POST'])
def fb_webhook():
    # Handle the initial handshake request.
    if flask.request.method == 'GET':
        if flask.request.args.get("hub.mode") == "subscribe" and flask.request.args.get("hub.challenge"):
            if not flask.request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
                return "Verification token mismatch", 403
            return flask.request.args["hub.challenge"], 200

        return "Hello world", 200

    # Get the request body as a dict, parsed from JSON.
    payload = flask.request.json

    # Handle an incoming message.
    for entry in payload['entry']:
        for event in entry['messaging']:
            if 'message' not in event:
                continue
            message = event['message']
            # Ignore messages sent by us.
            if message.get('is_echo', False):
                continue

            # Be a echo of messages with images.
            if 'sticker_id' in message:
                sender_id = event['sender']['id']
                sticker_id = message["sticker_id"]
                url_sticker = message["attachments"][0]["payload"]["url"]

                params = {
                    "access_token": os.environ["PAGE_ACCESS_TOKEN"]
                }
                response = requests.post(FACEBOOK_API_MESSAGE_SEND_URL,
                                         params=params,
                                         headers={'Content-Type': 'application/json'},
                                         json={'recipient': {'id': sender_id},
                                               'message': {'attachment': {'type': 'image',
                                                                          'payload': {'url': url_sticker}}}})
                if response.status_code != 200:
                    print(response.text)

            if not 'text' in message:
                continue

            # If the message has text the Bot wants to answer that
            sender_id = event['sender']['id']
            message_text = message['text']
            reply = handle_message(message_text, sender_id)

            if type(reply) == dict:
                params = {
                    "access_token": os.environ["PAGE_ACCESS_TOKEN"]
                }
                requests.post(FACEBOOK_API_MESSAGE_SEND_URL,
                              params=params,
                              headers={'Content-Type': 'application/json'},
                              json={'recipient': {'id': sender_id},
                                    'message': {'attachment': {'type': 'image',
                                                               'payload': reply}}})
            # if type(reply) == dict:
            #     params = {
            #         "access_token": os.environ["PAGE_ACCESS_TOKEN"]
            #     }
            #     requests.post(FACEBOOK_API_MESSAGE_SEND_URL,
            #                   params=params,
            #                   headers={'Content-Type': 'application/json'},
            #                   json={'recipient': {'id': sender_id},
            #                         'message': {'text': reply}})
            else:
                params = {
                    "access_token": os.environ["PAGE_ACCESS_TOKEN"]
                }
                requests.post(FACEBOOK_API_MESSAGE_SEND_URL,
                              params=params,
                              headers={'Content-Type': 'application/json'},
                              json={'recipient': {'id': sender_id},
                                    'message': {'text': reply}})

    # Return an empty response.
    return ''


if __name__ == '__main__':
    DEBUG = "NO_DEBUG" not in os.environ
    PORT = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
