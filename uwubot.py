from argparse import ArgumentParser
from base64 import b64encode
from collections import namedtuple
import random

import tweepy

Secret = namedtuple(
    "Secret",
    "apikey, apisecret, bearertoken, accesstoken, accesstokensecret"
)


def fuck_up_token(text, token, replacements):
    out = []
    i = 0
    while i < len(text):
        if text[i:].startswith(token):
            i += len(token)
            out.append(random.choice(replacements))
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def fuck_up_case(text, fuck_up_prob=0.05):
    out = []
    for char in text:
        if random.random() < fuck_up_prob:
            out.append(char.swapcase())
        else:
            out.append(char)
    return "".join(out)


def intersperse_emoji(text, fuck_up_prob=0.05):
    emoji = ["🤣", "🤪", "😱", "😋", "😤", "👀"]
    out = []
    for char in text:
        if random.random() < fuck_up_prob:
            if char == " ":
                out.append(" " + random.choice(emoji) + " ")
            else:
                out.append(char)
        else:
            out.append(char)
    return "".join(out)


def fuck_up_text(text):
    text = fuck_up_token(text, "s", ["th", "s", "s", "sd"])
    text = fuck_up_token(text, "n ", ["nd "])
    text = fuck_up_token(text, "S", ["Th", "S", "Ss"])
    text = fuck_up_token(text, "r", ["th", "dg", "l", "d", "w", "w", "w", "ww"])
    text = fuck_up_token(text, "R", ["Th", "Gdg", "L", "D"])
    text = fuck_up_token(text, ",", [" :PPP ", " UwU ", " XD ", "!!!!! ", " ^^ ", "ya~~", " nya~ "])
    text = fuck_up_token(text, ".", [" uwu ", " owo ", "O_O", "!!!!! ", " ^_^", " :3 ", " rawr X3 "])
    text = fuck_up_token(text, "kj", ["sj", "skj"])
    text = fuck_up_case(text)
    text = intersperse_emoji(text)
    while "  " in text:
        text = text.replace("  ", " ")
    return text


def get_tweets(api, victim):
    response = api.search(
        q=f"from:{victim}",
        tweet_mode="extended",
        include_entities=False,
        since_id=0,
    )
    return [tweet.full_text for tweet in response]


def post_tweet(api, text):
    result = api.update_status(text)
    return result


def authenticate():
    with open("secret.txt") as file:
        lines = list(file.read().strip().split("\n"))
    secret = Secret(*lines)
    auth = tweepy.OAuthHandler(secret.apikey, secret.apisecret)
    auth.set_access_token(secret.accesstoken, secret.accesstokensecret)
    api = tweepy.API(auth)
    return api


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-v", "--victim", required=True)
    args = parser.parse_args()

    api = authenticate()
    for status in get_tweets(api, args.victim):
        print("Original: ", status)

        # Try to ensure the text is short enough
        for attempt in range(100):
            fucked_up = fuck_up_text(status)
            if len(fucked_up) < 280:
                break
        else:
            print("Failed to find a short enough fucked up version")

        print("Fucked up: ", fucked_up)
        if input("Approve? ") == "yes":
            try:
                post_tweet(api, fucked_up)
            except Exception as exc:
                print("Got exception", exc)
