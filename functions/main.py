# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import firebase_admin
import google.cloud
import google.cloud.firestore

# import settings as settings
from firebase_functions import https_fn
from firebase_admin import initialize_app, credentials, firestore, storage
from openai import OpenAI
from elevenlabs import voices, generate

chat_gpt_client = OpenAI()

# firestore database
cred = credentials.Certificate("./ServiceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()
doc_ref = db.collection("stories")
# doc_ref = db.collection("stories").limit(2)
try:
    docs = doc_ref.get()
    for doc in docs:
        print("Doc Data:{}".format(doc.to_dict()))
except google.cloud.exceptions.NotFound:
    print("Missing data")

# firebase storage
bucket = storage.bucket()

# firebase app
app = initialize_app(cred, {"storageBucket": "playo-913ea.appspot.com"})


# generate story from inputs and return json of story & character descriptions
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
    pattern = r"Title: (.+?)"

    # Use re.search to find the match in the input string
    match = re.search(pattern, input_string)

    if match:
        title = match.group(1)
        print("Title:", title)
    else:
        title = ""
        print("Title not found.")


    response_character = generate_characters_json(response_story)
    print(response_story)
    print(response_character)
    
    response_object = {"story": response_story, "characters": response_character, "narrator_voice": "", "storyId":title}

    db_doc = doc_ref.add(response_object)

    response_object["document_id"] = db_doc.id

    return https_fn.Response.json(response_object)


# generate character descriptions from story
def generate_characters_json(story: str) -> str:
    completion = chat_gpt_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a world class story writer/author."},
            {
                "role": "user",
                "content": f'given the following story, give a general description of each character, as well as their age and gender. Format the response as a list JSON. The list should have the following structure: \n [ \n {{ \n "name": ..., \n "description": ..., \n "voice_description": ..., \n "age": ..., \n "gender": ... \n }}, \n ... \n ] \n\n Here is the story: "{story}"',
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
    audio = generate(text=story.story, voice=voice_id)
    audio_data = audio.data

    # upload to firebase storage
    blob = bucket.blob(f"{story.id}/{document_id}.mp3")
    blob.upload_from_string(audio_data, content_type="audio/mpeg")

    print("Audio file successfully uploaded to firebase storage")
