from pathlib import Path
from typing import List, Dict, Optional, Tuple
from pydub import AudioSegment, silence

def chunk_audio_with_timestamps(
    audio: AudioSegment,
    min_silence_len: int = 500,
    silence_thresh: Optional[int] = None,
    keep_silence: int = 200,
    min_chunk_ms: int = 3000,     # don't emit micro-chunks
    max_chunk_ms: int = 30000,    # keep chunks manageable for STT
    fallback_window_ms: int = 20000,
    overlap_ms: int = 250
) -> List[Dict]:
    """
    Split audio into chunks, returning metadata:
      [{"segment": AudioSegment, "start_ms": int, "end_ms": int}, ...]

    Strategy:
      1) Use silence to find speech ranges.
      2) Merge/clip ranges to respect min/max chunk size.
      3) If we can't find speech ranges, fall back to fixed windows with overlap.
    """
    # 0) Adaptive threshold if not provided (noise-floor aware)
    if silence_thresh is None:
        # pydub: more negative => quieter. audio.dBFS ≈ overall loudness.
        # Using ~14 dB below overall loudness is a decent starting point.
        silence_thresh = int(audio.dBFS - 14)

    # 1) Find non-silent ranges as [start, end] in ms
    ranges: List[List[int]] = silence.detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )

    # 2) If nothing detected, fall back to fixed windows with overlap
    if not ranges:
        chunks = []
        i = 0
        total = len(audio)
        step = fallback_window_ms - overlap_ms
        while i < total:
            start = max(0, i)
            end = min(total, i + fallback_window_ms)
            chunks.append({"segment": audio[start:end], "start_ms": start, "end_ms": end})
            if end == total:
                break
            i += step
        return chunks

    # 3) Collapse gaps shorter than min_silence_len and enforce min/max durations
    #    Start with raw speech ranges, then expand with keep_silence
    expanded: List[Tuple[int, int]] = []
    for start, end in ranges:
        start = max(0, start - keep_silence)
        end = min(len(audio), end + keep_silence)
        if not expanded:
            expanded.append((start, end))
        else:
            prev_start, prev_end = expanded[-1]
            # If new range overlaps or is very close, merge
            if start <= prev_end + min_silence_len:
                expanded[-1] = (prev_start, max(prev_end, end))
            else:
                expanded.append((start, end))

    # 4) Break overly long segments into fixed windows with small overlap
    def split_long(start: int, end: int) -> List[Tuple[int, int]]:
        out = []
        length = end - start
        if length <= max_chunk_ms:
            return [(start, end)]
        step = max_chunk_ms - overlap_ms
        i = start
        while i < end:
            s = i
            e = min(end, i + max_chunk_ms)
            out.append((s, e))
            if e == end:
                break
            i += step
        return out

    bounded: List[Tuple[int, int]] = []
    for s, e in expanded:
        segs = split_long(s, e)
        for bs, be in segs:
            # Drop tiny fragments
            if (be - bs) >= min_chunk_ms:
                bounded.append((bs, be))

    # 5) Materialize segments
    chunks: List[Dict] = []
    for s, e in bounded:
        chunks.append({"segment": audio[s:e], "start_ms": s, "end_ms": e})

    return chunks
