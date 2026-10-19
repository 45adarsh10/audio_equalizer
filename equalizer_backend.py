import time
from dataclasses import dataclass

import numpy as np
import soundfile as sf
from scipy import signal


@dataclass
class AudioData:
    samples: np.ndarray
    sample_rate: int


class DigitalAudioEqualizer:
    def __init__(self):
        self.bass_hz = 250.0
        self.mid_low_hz = 250.0
        self.mid_high_hz = 2000.0
        self.treble_hz = 2000.0

    def load_audio(self, path):
        """Load WAV or MP3 audio as float32 samples using libsndfile."""
        try:
            samples, sample_rate = sf.read(
                path, dtype="float32", always_2d=True
            )
        except (sf.LibsndfileError, RuntimeError) as error:
            extension = str(path).lower().rsplit(".", 1)[-1]
            if extension == "mp3":
                raise ValueError(
                    "This MP3 could not be decoded by the installed SoundFile/"
                    "libsndfile. Install the project requirements (SoundFile "
                    "0.13.1 or newer with MP3 support), then restart the "
                    f"application. Decoder details: {error}"
                ) from error
            raise ValueError(f"Could not read audio file: {error}") from error

        if samples.size == 0:
            raise ValueError("The selected audio file contains no samples.")
        return AudioData(samples, sample_rate)

    def save_audio(self, path, samples, sample_rate):
        """Save processed audio as a 16-bit PCM WAV file."""
        samples = np.asarray(samples, dtype=np.float32)
        samples = np.nan_to_num(samples)
        samples = np.clip(samples, -1.0, 1.0)
        sf.write(path, samples, sample_rate, subtype="PCM_16")

    def mono(self, samples):
        """Convert stereo audio to mono for analysis."""
        samples = np.asarray(samples)
        if samples.ndim == 1:
            return samples
        return np.mean(samples, axis=1)

    def waveform(self, samples, sample_rate):
        samples = self.mono(samples)
        times = np.arange(len(samples)) / sample_rate
        return times, samples

    def spectrum(self, samples, sample_rate):
        samples = self.mono(samples)

        if len(samples) == 0:
            raise ValueError("Audio file is empty.")

        window = np.hanning(len(samples))
        spectrum = np.fft.rfft(samples * window)
        frequencies = np.fft.rfftfreq(
            len(samples), d=1.0 / sample_rate
        )

        magnitude = np.abs(spectrum)
        magnitude_db = 20 * np.log10(
            np.maximum(magnitude, 1e-10)
        )

        return frequencies, magnitude_db

    def design_filters(self, sample_rate, filter_type="FIR"):
        nyquist = sample_rate / 2.0

        if nyquist <= self.mid_high_hz:
            raise ValueError(
                "Sample rate is too low for the selected frequency bands."
            )

        filter_type = filter_type.upper()

        if filter_type == "FIR":
            taps = 501

            bass = signal.firwin(
                taps, self.bass_hz,
                fs=sample_rate, pass_zero="lowpass"
            )
            mid = signal.firwin(
                taps, [self.mid_low_hz, self.mid_high_hz],
                fs=sample_rate, pass_zero="bandpass"
            )
            treble = signal.firwin(
                taps, self.treble_hz,
                fs=sample_rate, pass_zero="highpass"
            )

            return {
                "bass": ("fir", bass),
                "mid": ("fir", mid),
                "treble": ("fir", treble),
            }

        elif filter_type == "IIR":
            order = 4

            bass = signal.butter(
                order, self.bass_hz,
                fs=sample_rate, btype="lowpass",
                output="sos"
            )
            mid = signal.butter(
                order, [self.mid_low_hz, self.mid_high_hz],
                fs=sample_rate, btype="bandpass",
                output="sos"
            )
            treble = signal.butter(
                order, self.treble_hz,
                fs=sample_rate, btype="highpass",
                output="sos"
            )

            return {
                "bass": ("sos", bass),
                "mid": ("sos", mid),
                "treble": ("sos", treble),
            }

        else:
            raise ValueError("filter_type must be 'FIR' or 'IIR'")

    def process(
        self,
        samples,
        sample_rate,
        bass_db=0.0,
        mid_db=0.0,
        treble_db=0.0,
        filter_type="FIR",
        normalize=False,
    ):
        start_time = time.perf_counter()

        samples = np.asarray(samples, dtype=np.float32)

        if samples.ndim == 1:
            samples = samples[:, None]

        if samples.ndim != 2 or samples.shape[0] == 0:
            raise ValueError("Invalid or empty audio samples.")

        filters = self.design_filters(sample_rate, filter_type)

        gains = {
            "bass": 10 ** (bass_db / 20.0),
            "mid": 10 ** (mid_db / 20.0),
            "treble": 10 ** (treble_db / 20.0),
        }

        output = np.zeros_like(samples, dtype=np.float64)

        for band_name, (kind, coefficients) in filters.items():
            filtered_channels = []

            for channel in range(samples.shape[1]):
                channel_data = samples[:, channel]

                if kind == "fir":
                    filtered = signal.lfilter(
                        coefficients, [1.0], channel_data
                    )
                else:
                    filtered = signal.sosfilt(
                        coefficients, channel_data
                    )

                filtered_channels.append(filtered)

            band_output = np.column_stack(filtered_channels)
            output += gains[band_name] * band_output

        if normalize:
            peak = np.max(np.abs(output))
            if peak > 0:
                output = output / peak * 0.99

        output = output.astype(np.float32)

        processing_time = time.perf_counter() - start_time
        peak_level = float(np.max(np.abs(output)))

        info = {
            "filter_type": filter_type.upper(),
            "sample_rate": sample_rate,
            "duration_seconds": len(samples) / sample_rate,
            "processing_time_seconds": processing_time,
            "peak_level": peak_level,
            "clipping_risk": peak_level > 1.0,
        }

        return output, info

    def filter_response(self, sample_rate, filter_type="FIR"):
        filters = self.design_filters(sample_rate, filter_type)
        responses = {}

        for name, (kind, coefficients) in filters.items():
            if kind == "fir":
                frequencies, response = signal.freqz(
                    coefficients, worN=2048, fs=sample_rate
                )
            else:
                frequencies, response = signal.sosfreqz(
                    coefficients, worN=2048, fs=sample_rate
                )

            magnitude_db = 20 * np.log10(
                np.maximum(np.abs(response), 1e-10)
            )

            responses[name] = (frequencies, magnitude_db)

        return responses