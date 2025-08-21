from pydub.silence import detect_nonsilent
from pydub import AudioSegment

def trim_silence(in_path: str, silence_thresh: int = -40, min_silence_len: int = 500) -> str:
    """
    Trim leading and trailing silence from an audio file.
    
    - silence_thresh: volume threshold in dBFS (default: -40 dBFS)
    - min_silence_len: how long silence must last to be considered silence (ms)
    
    Returns path to trimmed file.
    """
    audio = AudioSegment.from_file(in_path)

    # Find non-silent chunks [(start, end), ...]
    nonsilent_ranges = detect_nonsilent(audio, 
    min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    if not nonsilent_ranges:
        print("No speech detected — returning original file")
        return in_path

    # Keep only the non-silent range from first speech to last speech
    start_trim = nonsilent_ranges[0][0]
    end_trim = nonsilent_ranges[-1][1]
    trimmed = audio[start_trim:end_trim]

    out_path = str(Path(in_path).with_suffix(".trimmed.wav"))
    trimmed.export(out_path, format="wav")
    return out_path
