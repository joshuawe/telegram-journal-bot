"""This script does transcription of audio files via Huggingface API."""
import logging
import json
from pathlib import Path
import time

import requests
from telegram.ext import ContextTypes


import utils
import openai_api

logger = logging.getLogger(__name__)



async def transcribe_from_file_huggingface(filepath: Path, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    
    # get Huggingface API set up
    API_TOKEN = utils.get_huggingface_token()
    model_name = utils.get_speech2text_model_name()
    RETRIES = utils.get_config()['huggingface']['retries']
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    logger.info(f"Transcribing with Huggingface API. Model: {model_name}")
    
    # read audio file
    with open(filepath, "rb") as f:
        data = f.read()
        
    n_try=1
    while n_try <= RETRIES:
        # query Huggingface API
        response = requests.request("POST", API_URL, headers=headers, data=data)
        response = json.loads(response.content.decode("utf-8"))
    
        if 'error' in response.keys() and 'estimated_time' in response.keys():
            logger.error(f"Error in transcribe_from_file. The Hugginface Inference API request returned: {response}")
            await context.bot.send_message(chat_id=chat_id, text=f"Error: {response} \n\n**Retrying ({n_try}/{RETRIES})**")
            # wait for estimated time
            time.sleep(response['estimated_time'] * 0.5)
            n_try += 1
            if n_try > RETRIES:
                await context.bot.send_message(chat_id=chat_id, text=f"**Retries exhausted.**") 
        else:
            break
    
    return response

async def transcribe_from_file_openai(file_path: Path, *args):
    try:
        print("Transcribing with OpenAI API. transcribe_from_file_openai")
        open_client = openai_api.OpenAiCLient(utils.get_openai_token())
        transcription = open_client.transcribe(file_path)
        response = {'text': transcription.text}
    except Exception as e:
        print(e)
        return {'error': e}
        
    return response


