
import vosk
from pydub import AudioSegment
model = vosk.Model("path_to_urdu_english_model")
from typing import List, Dict, Optional
from transliterations import URDU_TO_ROMAN
import json

import numpy as np

def transcribe_chunk(audio_chunk: AudioSegment):
    rec = vosk.KaldiRecognizer(model, audio_chunk.frame_rate)
    # feed raw audio
    rec.AcceptWaveform(audio_chunk.raw_data)
    result = rec.Result()
    # return list of {"word": str, "confidence": float, "start_ms": int, "end_ms": int}
    return result



def extract_word_audio(chunk_audio: bytes, start_s: float, end_s: float, sample_rate: int = 16000) -> bytes:

    # Convert raw PCM16 (bytes) → numpy array
    audio_np = np.frombuffer(chunk_audio, dtype=np.int16)

    # Convert times (s) → sample indices
    start_idx = int(start_s * sample_rate)
    end_idx = int(end_s * sample_rate)

    # Slice the word segment
    word_np = audio_np[start_idx:end_idx]

    # Convert back to raw PCM16
    return word_np.tobytes()

def select_bilingual_transcription(
    words: List[Dict],
    vosk_model,
    urdu_model,
    threshold: float = 0.65
) -> List[str]:

    # Args:
    #     words: List of word dicts from initial Vosk transcription.
    #     vosk_model: Preloaded Vosk model for Roman Urdu + English.
    #     urdu_model: Preloaded Urdu STT model.
    #     threshold: Confidence threshold for direct acceptance.

    final_transcript = []
    ambiguous = []

    for w in words:
        if w["confidence"] >= threshold:
            final_transcript.append(w["word"])
        else:
            ambiguous.append(w)

    # 2: resolve ambiguous words
    for w in ambiguous:
        start_ms, end_ms = w["start_ms"], w["end_ms"]
        segment_audio = w.get("audio_segment")  

        # Run Urdu model on this segment
        urdu_result = urdu_model.transcribe(segment_audio)
        urdu_word = transliterate_urdu_to_roman(urdu_result)

        # Compare confidence (Vosk vs Urdu-transliterated)
        vosk_conf = w["confidence"]
        urdu_conf = urdu_result.get("confidence", 0.0)

        if urdu_conf > vosk_conf:
            final_transcript.append(urdu_word)
        else:
            final_transcript.append(w["word"])

    return final_transcript


def transliterate_urdu_to_roman(urdu_text: str) -> str:
    """
    Convert Urdu script to basic Roman Urdu.
    - Numbers, punctuation, and English letters are preserved.
    """
    roman = []
    for char in urdu_text:
        # Use mapping if available, else keep original
        roman.append(URDU_TO_ROMAN.get(char, char))
    return "".join(roman)

def transcribe_with_fallback(audio_chunk: bytes, rec_en, rec_ur, threshold: float = 0.65, sample_rate: int = 16000):
    """
    Transcribe audio with English model, fallback to Urdu if confidence is low.
    - audio_chunk: PCM16 little-endian bytes (3s chunk, mono, 16kHz)
    - rec_en: English Vosk recognizer
    - rec_ur: Urdu Vosk recognizer
    - threshold: min confidence for accepting English result
    - sample_rate: audio sample rate (default 16kHz)

    Returns: list of chosen words
    """
    final_words = []

    # Step 1: English transcription
    rec_en.AcceptWaveform(audio_chunk)
    result_en = json.loads(rec_en.Result())

    if "result" not in result_en:
        return final_words  # No words recognized

    for w in result_en["result"]:
        word_text = w["word"]
        word_conf = w["conf"]
        ur_conf=0
        if word_conf >= threshold:
            final_words.append(word_text)
        else:
            word_start = w["start"]
            word_end = w["end"]

            word_audio = extract_word_audio(audio_chunk, word_start, word_end, sample_rate)

            # Run Urdu recognizer
            rec_ur.AcceptWaveform(word_audio)
            result_ur = json.loads(rec_ur.Result())

            if "result" in result_ur and len(result_ur["result"]) > 0:
                ur_word = result_ur["result"][0]["word"]
                ur_conf = result_ur["result"][0]["conf"]

                # Choose whichever has higher confidence
        if ur_conf > word_conf:
            final_words.append(ur_word)
        else:
            final_words.append(word_text)


    return final_words