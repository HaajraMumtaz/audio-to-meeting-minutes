TARGET_SR = 16000 # 16 kHz
TARGET_CHANNELS = 1 # mono
TARGET_WIDTH_BYTES = 2 # 16-bit PCM
DEFAULT_SILENCE_THRESH_DBFS = -35 # adjustable
DEFAULT_MIN_SILENCE_LEN_MS = 300 # consider segments of >=300 ms as silence
DEFAULT_KEEP_SILENCE_MS = 200 #so words aren't chopped
DEFAULT_SNR_THRESHOLD_DB = 15 # if below - consider denoise
DEFAULT_RMS_TARGET_DBFS = -20
MAX_INT16 = 32767

from pydub import AudioSegment
import numpy as np
from pathlib import Path
from typing import Optional

def _ensure_wav_16k_mono_16bit(seg: AudioSegment) -> AudioSegment:
    seg = seg.set_channels(TARGET_CHANNELS)
    seg = seg.set_frame_rate(TARGET_SR)
    seg = seg.set_sample_width(TARGET_WIDTH_BYTES)
    return seg


def standardize_audio(in_path: str | Path, out_path: Optional[str | Path] = None) -> str:
    """Convert any supported input audio to WAV (PCM 16-bit, 16kHz, mono).
    
    Returns path to standardized file.
    """
    in_path = str(in_path)
    audio = AudioSegment.from_file(in_path)   # load audio (any format)
    audio = _ensure_wav_16k_mono_16bit(audio) # convert to canonical format

    if out_path is None:
        out_path = str(Path(in_path).with_suffix(".16k_mono.wav"))
    else:
        out_path = str(out_path)

    audio.export(out_path, format="wav") # save as clean WAV
    return out_path
def _audiosegment_to_numpy(seg: AudioSegment) -> np.ndarray:
    samples = np.array(seg.get_array_of_samples())
    if seg.channels > 1:
        samples = samples.reshape((-1, seg.channels)).mean(axis=1)
    return samples.astype(np.int16)