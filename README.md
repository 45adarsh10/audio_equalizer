# Digital Audio Equalizer

A desktop audio equalizer built with Python and Tkinter. Load WAV or MP3 audio, adjust bass, midrange, and treble, choose FIR or IIR filtering, compare waveform and FFT plots, and export the processed result as a WAV file.

## Features

- Spotify-inspired graphical interface
- WAV and MP3 file loading
- Bass, midrange, and treble gain controls from −12 dB to +12 dB
- FIR and IIR equalizer filter options
- Waveform and frequency-spectrum comparison embedded in the GUI
- Processed audio export as 16-bit PCM WAV

## Requirements

- Python 3.10 or newer recommended
- NumPy
- SciPy
- SoundFile with MP3 decoding support
- Matplotlib
- Tkinter (included with most standard Windows Python installations)

The versions in `requirements.txt` are minimums. Installing from that file lets pip select the latest compatible releases that meet those minimums. MP3 decoding also depends on the SoundFile/libsndfile build installed in your Python environment. Recent official Windows SoundFile wheels include MP3 support.

## Project files

Keep the Python files and `requirements.txt` together in the project directory:

```text
DigitalAudioEqualizer/
├── equalizer_backend.py
├── equalizer_gui_spotify.py
├── requirements.txt
└── README.md
```

## Setup on Windows with VS Code

1. Open the project folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Install the latest compatible dependency versions listed in `requirements.txt`:

   ```powershell
   py -m pip install --upgrade pip
   py -m pip install -r requirements.txt
   ```

4. Launch the equalizer GUI:

   ```powershell
   py equalizer_gui_spotify.py
   ```

## Using the application

1. Click **Load Audio** and choose a `.wav` or `.mp3` file.
2. Select **FIR** or **IIR** filtering.
3. Adjust the Bass, Mid, and Treble sliders.
4. Click **Apply Equalizer** to process the audio.
5. Use **Waveform & FFT** or **Visualize** to display the original and processed plots in the right-side panel.
6. Click **Save WAV** to export the processed audio.

The output is saved as WAV even when the input is MP3. This avoids requiring an MP3 encoder and keeps the exported result in a broadly supported audio format.

## Troubleshooting

### MP3 file does not load

Upgrade SoundFile in the same Python installation used to run the GUI:

```powershell
py -m pip install --upgrade soundfile
```

Restart the GUI after installing. If decoding still fails, the installed SoundFile/libsndfile build may not have MP3 support.

### `ModuleNotFoundError`

Install the project dependencies again:

```powershell
py -m pip install -r requirements.txt
```

### GUI will not start

Check that Tkinter is available in your Python installation and run the GUI from the project folder so it can find `equalizer_backend.py`.

## Notes

- `equalizer_gui_spotify.py` imports `DigitalAudioEqualizer` from `equalizer_backend.py`; keep these files in the same folder.
- FIR and IIR processing retain the input sample rate and channel layout.
- The backend reports when an output peak may clip. The WAV save method clips samples to the valid PCM audio range.
