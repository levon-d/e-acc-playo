# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
from openai import OpenAI
import settings

app = initialize_app()
chat_gpt_client = OpenAI(
    api_key = settings.OPENAI_API_KEY
)


#
#
@https_fn.on_request()
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    text = req.args.get("text")
    age_rating = req.args.get("ageRating")
    story_line = req.args.get("sotyLine")
    word_count = req.args.get("wordCount")



    return https_fn.Response("Hello world!")