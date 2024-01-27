# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from openai import OpenAI
import settings as settings

app = initialize_app()
chat_gpt_client = OpenAI()


#
#
@https_fn.on_request()
def trythis(req: https_fn.Request) -> https_fn.Response:
    text = req.args.get("text")
    theme = req.args.get("theme")
    age_rating = req.args.get("age_rating")
    # story_line = req.args.get("storyLine")
    word_count = req.args.get("word_ount")

    completion = chat_gpt_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a world class story writer/author."},
            {
                "role": "user",
                "content": f"Write a story with genre: {theme} and age rating: {age_rating} with the following story line: {text}. It should be approximately {word_count} number of words",
            },
        ],
    )
    response = completion.choices[0].message 
    print(completion.choices[0].message)

    return https_fn.Response(response)
