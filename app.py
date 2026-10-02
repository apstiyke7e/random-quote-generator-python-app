import os
import secrets

from flask import Flask, render_template, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

QUOTES = (
    {
        "text": "Small steps still move you somewhere new.",
        "author": "A note to begin",
    },
    {
        "text": "Make room for the things you have not imagined yet.",
        "author": "A note to begin",
    },
    {
        "text": "Curiosity is a compass that works in every weather.",
        "author": "A note to begin",
    },
    {
        "text": "A little patience can turn a rough draft into a direction.",
        "author": "A note to begin",
    },
    {
        "text": "Pay attention: ordinary days are where a life is made.",
        "author": "A note to begin",
    },
    {
        "text": "You do not need the whole map to take the next turn.",
        "author": "A note to begin",
    },
    {
        "text": "Begin before certainty arrives; it is often running late.",
        "author": "A note to begin",
    },
)


@app.get("/")
def home():
    previous_quote = session.get("quote")
    choices = [quote for quote in QUOTES if quote["text"] != previous_quote]
    quote = secrets.choice(choices)
    session["quote"] = quote["text"]
    return render_template("index.html", quote=quote)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")