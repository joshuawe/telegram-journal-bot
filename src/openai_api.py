from pathlib import Path

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
RETRIES = 6

import utils


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(RETRIES))
def transcribe(file_path: Path, model_name: str="whisper-1"):
    audio_file = open(file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model=model_name,
        file=audio_file
    )  
    return transcript


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(RETRIES))
def chat_completion(user_message: str, model_name: str="gpt-3.5-turbo", context: str="You are a helpful assistant."):
    completion = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "system", "content": context},
        {"role": "user", "content": user_message}
    ]
    )
    return completion.choices[0].message


if __name__ == "__main__":
    client = openai.OpenAI(api_key=utils.get_openai_token())
    print(client)
    
    audio_file = Path(r"C:\Users\joshu\LRZ_Sync_Share\Joshua\Programming\telegram-journal-bot\voice_messages\AwACAgIAAxkBAAPzZZsmlQjGJ28zg5KNI_aGM3bQ7uoAAuU8AAJhkuBI88yqfcGKZyQ0BA.ogg")
    
    transcript = transcribe(audio_file)
    print(transcript)

