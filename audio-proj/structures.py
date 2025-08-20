from dataclasses import dataclass

@dataclass
class AudioStats:
    duration_sec: float
    channels: int
    frame_rate: int
    sample_width_bytes: int


    rms_dbfs: float
    peak_dbfs: float
    clipping_ratio: float # fraction of samples at full-scale (|x| >= 32767)


    silence_ratio: float # fraction of duration detected as silence
    snr_db: float # rough estimate using frame energy distribution


def pretty(self) -> str:
    return (
f"duration: {self.duration_sec:.2f}s | chans: {self.channels} | sr: {self.frame_rate} Hz | width: {self.sample_width_bytes*8}-bit\n"
f"rms: {self.rms_dbfs:.1f} dBFS | peak: {self.peak_dbfs:.1f} dBFS | clipping: {self.clipping_ratio*100:.2f}%\n"
f"silence: {self.silence_ratio*100:.1f}% | SNR≈ {self.snr_db:.1f} dB"
)