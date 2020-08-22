# uwubot

Reads tweets from a victim account, does some string manipulation to make it sound extremely stupid, and tweets the result

# Setup

```
pip install -r requirements.txt
```

Set up a developer account and create a file called `secrets.json` with credentials:

```
{
    "consumer_key": "",
    "consumer_key_secret": "",
    "bearer_token": "",
    "access_token": "",
    "access_token_secret": ""
}
```

# Example session

Run the script with `-v` set to the username of the victim.
You will be presented with the original and fucked up versions of each tweet.
To send the tweet you must write "yes" in response to the "Approve?" prompt.

```
$ python uwubot.py -v realDonaldTrump
Original:  In New Jersey they want you to certify that you asked for the Universal Mail-In Ballot that they sent you. But you never asked for it. Disaster in the wings!
Fucked up:  Ind New JedGsey they want you to cewtiFy tHat you asked fowW thE 👀 UniVewsdal Mail-INd Ballot that thEy seNt youO_O But you nevew asked foww it owo Dithasteww ind the wIngth!
Approve? no
Original:  Many doctors and studies disagree with this! https://t.co/fpLVJZMvHS
Fucked up:  Many doctoths aNd thtudieTh dithagdee with this! https://t owo co/fpLVJzMvHS
Approve? no
```

and so on.
