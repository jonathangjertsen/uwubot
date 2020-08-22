from argparse import ArgumentParser
from base64 import b64encode
from collections import namedtuple
from copy import deepcopy
from pathlib import Path
import random
import json
from typing import List, Dict

import tweepy

Secret = namedtuple(
    "Secret",
    "consumer_key, consumer_key_secret, bearer_token, access_token, access_token_secret"
)


def fuck_up_token(text: str, token: str, replacements: List[str]) -> str:
    """
    Replaces each <token> in <text> with a random element from <replacements>
    """
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


def fuck_up_case(text: str, fuck_up_prob: float) -> str:
    """
    Swaps the case of <text> with probability <fuck_up_prob> for each character
    """
    out = []
    for char in text:
        if random.random() < fuck_up_prob:
            out.append(char.swapcase())
        else:
            out.append(char)
    return "".join(out)


def intersperse_emoji(text: str, emoji: List[str], fuck_up_prob: float) -> str:
    """
    Adds an emoji selected from <emoji> into <text> with
    probability <fuck_up_prob> for each space in the original text
    """
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


def read_config(config_filename: str) -> dict:
    """
    Reads a configuration file and takes care of inheritance
    """
    # Read the file
    with open(config_filename, "rb") as config_file:
        filebytes = config_file.read()
    config = json.loads(filebytes.decode("utf-8"))

    # Do inheritance
    if config["inherit"] is not None:
        # Read the config file pointed to by the inherit field
        parent = Path(config_filename).parent / config["inherit"]
        parent_config = read_config(parent)

        # Merge the replacements
        # If both configs define a replacement, merge them
        # If only one or the other defines a replacement, add that too
        merged_replacements = []
        for replacement_new in config["replacements"]:
            for replacement_parent in parent_config["replacements"]:
                if replacement_parent["original"] == replacement_new["original"]:
                    merged_replacements.append({
                        "original": replacement_new["original"],
                        "replacements": replacement_parent["replacements"] + replacement_new["replacements"]
                    })
                    break
            else:
                merged_replacements.append(replacement_new)
        for replacement_parent in parent_config["replacements"]:
            for replacement_new in config["replacements"]:
                if replacement_parent["original"] == replacement_new["original"]:
                    break
            else:
                merged_replacements.append(replacement_parent)

        # Do the other mergers inline
        config = {
            "replacements": merged_replacements,
            "emoji": config.get("emoji", []) + parent_config["emoji"],
            "emoji_prob": config.get("emoji_prob", parent_config["emoji_prob"]),
            "case_prob": config.get("case_prob", parent_config["case_prob"])
        }
    return config


def fuck_up_text(text: str, config_filename: str) -> str:
    """
    Does all the fucking up to <text> according to the configuration stored in <config_filename>
    """
    config = read_config(config_filename)

    for replacement in config["replacements"]:
        text = fuck_up_token(
            text,
            replacement["original"],
            replacement["replacements"],
        )

    text = fuck_up_case(
        text,
        config["case_prob"]
    )
    text = intersperse_emoji(
        text,
        config["emoji"],
        config["emoji_prob"]
    )
    while "  " in text:
        text = text.replace("  ", " ")
    return text


def get_tweets(api: tweepy.API, victim: str) -> List[str]:
    """
    Returns the available tweets from the victim
    """
    response = api.search(
        q=f"from:{victim}",
        tweet_mode="extended",
        include_entities=False,
        since_id=0,
    )
    return [tweet.full_text for tweet in response]


def post_tweet(api: tweepy.API, text: str):
    """
    Posts the tweet
    """
    result = api.update_status(text)
    return result


def authenticate(secret_filename: str) -> tweepy.API:
    """
    Returns an object that can do authenticated API queries
    """
    with open(secret_filename) as file:
        secret = Secret(**json.load(file))
    auth = tweepy.OAuthHandler(secret.consumer_key, secret.consumer_key_secret)
    auth.set_access_token(secret.access_token, secret.access_token_secret)
    api = tweepy.API(auth)
    return api


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-v", "--victim", required=True)
    parser.add_argument("-s", "--secret", required=True)
    parser.add_argument("-r", "--replacements", required=True)
    args = parser.parse_args()

    api = authenticate(args.secret)
    for status in get_tweets(api, args.victim):
        print("Original: ", status)

        # Try to ensure the text is short enough
        for attempt in range(100):
            fucked_up = fuck_up_text(status, args.replacements)
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
