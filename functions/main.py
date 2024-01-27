# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore, db, storage
import google.cloud.firestore
from openai import OpenAI
import settings as settings
from elevenlabs import generate, voices

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

    response_story = completion.choices[0].message.content
    response_character = generate_characters_json(response_story)
    print(response_story)
    print(response_character)
    
    response_object = {
        "story": response_story,
        "characters": response_character
    }

    return https_fn.Response(response_object)

def generate_characters_json(story: str) -> str:

    completion = chat_gpt_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a world class story writer/author."},
            {
                "role": "user",
                "content": f"given the following story, give a general description of each character, as well as their age and gender. Format the response as a list JSON. The list should have the following structure: \n [ \n {{ \n \"name\": ..., \n \"description\": ..., \n \"voice_description\": ..., \n \"age\": ..., \n \"gender\": ... \n }}, \n ... \n ] \n\n Here is the story: \"{story}\"",
            },
        ],
    )

    response = completion.choices[0].message.content

    return response

@https_fn.on_request()
def generate_narration(req: https_fn.Request) -> https_fn.Response:
    data = req.get_json()
    voice_id = data.get("voice_id")
    # story_id = data.get("story_id")
    document_id = data.get("document_id")
    firestore_client: google.cloud.firestore.Client = firestore.client()
    story = firestore_client.collection("stories").document(document_id).get().to_dict()
    audio = generate(
        text=story.story,
        voice=voice_id
    )
    audio_data = audio.data

    # upload to firebase storage
    bucket = storage.bucket()
    blob = bucket.blob(f"{story.id}/{document_id}.mp3")
    blob.upload_from_string(audio_data, content_type="audio/mpeg")

    print("Audio file successfully uploaded to firebase storage")

    