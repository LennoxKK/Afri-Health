import os
import whisper
import logging

logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self, model_size="base"):
        """
        Initializes the transcriber with a specific model size.
        """
        self.model = whisper.load_model(model_size)
        logger.info(f"Loaded Whisper model: {model_size}")

    def transcribe_audio(self, audio_path, language="Portuguese"):
        """
        Transcribes the audio file specified by audio_path and returns the transcription text.

        Args:
            audio_path: Path to the audio file.
            language: Language used for transcription (default: "Portuguese").

        Returns:
            str: Transcribed text.
        """
        try:
            logger.info(f"Starting transcription for file: {audio_path}")
            result = self.model.transcribe(audio_path, language=language)
            transcription_text = result["text"]
            logger.info(f"Transcription successful: {transcription_text}")
            return transcription_text
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {str(e)}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    def save_transcription(self, transcription_text, output_file):
        """
        Saves the transcription text to a .txt file.

        Args:
            transcription_text: Text to save.
            output_file: Path to the output .txt file.
        """
        try:
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(transcription_text)
            logger.info(f"Transcription saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save transcription: {str(e)}")
            raise Exception(f"Failed to save transcription: {str(e)}")