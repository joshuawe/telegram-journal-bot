"""This script does transcription of audio files via Huggingface API."""
import logging
import json
from pathlib import Path

import requests

import utils

logger = logging.getLogger(__name__)



def transcribe_from_file(filepath: Path):
    
    # get Huggingface API set up
    API_TOKEN = utils.get_huggingface_token()
    model_name = utils.get_speech2text_model_name()
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    logger.info(f"Transcribing with Huggingface API. Model: {model_name}")
    
    # read audio file
    with open(filepath, "rb") as f:
        data = f.read()
        
    # query Huggingface API
    response = requests.request("POST", API_URL, headers=headers, data=data)
    
    result = json.loads(response.content.decode("utf-8"))
    
    if 'error' in result.keys():
        logger.error(f"Error in transcribe_from_file. The Hugginface Inference API request returned: {result}")
    
    return result


