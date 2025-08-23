# Pseudocode / high-level
import vosk
from pydub import AudioSegment
model = vosk.Model("path_to_urdu_english_model")
from typing import List, Dict, Optional
from transliterations import URDU_TO_ROMAN

def transcribe_chunk(audio_chunk: AudioSegment):
    rec = vosk.KaldiRecognizer(model, audio_chunk.frame_rate)
    # feed raw audio
    rec.AcceptWaveform(audio_chunk.raw_data)
    result = rec.Result()
    # return list of {"word": str, "confidence": float, "start_ms": int, "end_ms": int}
    return result



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
