"""
Azure AI Speech Wrapper

Transcribes doctor dictations into accurate text using Microsoft Foundry's Speech-to-Text.

Requires: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
"""

import os
import azure.cognitiveservices.speech as speechsdk
from typing import Optional

def is_configured() -> bool:
    return bool(os.getenv("AZURE_SPEECH_KEY") and os.getenv("AZURE_SPEECH_REGION"))

def transcribe_audio_file(audio_file_path: str) -> Optional[str]:
    """
    Sends an audio file to Azure AI Speech for transcription.
    Returns the transcribed text, or None if configured incorrectly.
    """
    if not is_configured():
        return None
        
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"), 
            region=os.getenv("AZURE_SPEECH_REGION")
        )
        # Assuming the UI uploads standard wav files
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )
        
        # Perform recognition
        result = speech_recognizer.recognize_once_async().get()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("Azure Speech: No speech could be recognized")
            return ""
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Azure Speech Canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return None
            
    except Exception as e:
        print(f"Azure AI Speech error: {e}")
        return None
