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


# generate story from inputs
@https_fn.on_request()
def generate_story(req: https_fn.Request) -> https_fn.Response:
    data = req.get_json()
    text = data.get("text")
    theme = data.get("theme")
    age_rating = data.get("age_rating")
    word_count = data.get("word_count")

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

    return https_fn.Response(response.content)

def generate_characters_json(req: https_fn.Request) -> https_fn.Response:
    data = req.get_json()
    story = data.get("story")

    completion = chat_gpt_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a world class story writer/author."},
            {
                "role": "user",
                "content": f"given the following story, give a general description of each character, as well as their age and gender. Format the response as a JSON. Here is the story: \"{story}\"",
            },
        ],
    )

    response = completion.choices[0].message
    print(completion.choices[0].message)

    return https_fn.Response(response.content)
