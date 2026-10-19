import os
import tkinter as tk
from tkinter import filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from equalizer_backend import DigitalAudioEqualizer

BG = "#0b0f12"
SIDEBAR = "#080b0e"
PANEL = "#141a1f"
DARK = "#101519"
BORDER = "#263139"
TEXT = "#f4f7f8"
MUTED = "#a7b1bb"
GREEN = "#1ed760"
PURPLE = "#a970ff"


class AudioEqualizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Audio Equalizer")
        self.root.geometry("1180x790")
        self.root.minsize(950, 650)
        self.root.configure(bg=BG)

        self.eq = DigitalAudioEqualizer()
        self.audio_data = None
        self.processed_audio = None
        self.sample_rate = None
        self.file_path = None
        self.plot_canvas = None

        self._build_ui()

    def card(self, parent, **kwargs):
        return tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
            **kwargs
        )

    def button(self, parent, text, command, primary=False):
        bg = GREEN if primary else "#263039"
        fg = "#06120a" if primary else TEXT
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground="#4be580" if primary else "#34414b",
            activeforeground=fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=10
        )

    def _build_ui(self):
        # Sidebar without the round logo or Load Audio/Equalizer entries.
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Audio Equalizer",
            bg=SIDEBAR,
            fg=TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=20, pady=(28, 30))

        self.nav_item(sidebar, "⌂", "Home", active=True)
        self.nav_item(
            sidebar, "∿", "Visualize", command=self.show_graphs
        )

        tk.Frame(sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=14, pady=22
        )
        tk.Label(
            sidebar,
            text="NOW LOADED",
            bg=SIDEBAR,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=20)

        self.sidebar_track = tk.Label(
            sidebar,
            text="No audio loaded",
            bg=SIDEBAR,
            fg=TEXT,
            font=("Segoe UI", 10),
            wraplength=170,
            justify="left"
        )
        self.sidebar_track.pack(anchor="w", padx=20, pady=(12, 4))

        self.sidebar_info = tk.Label(
            sidebar,
            text="Choose a WAV or MP3 file to begin",
            bg=SIDEBAR,
            fg=MUTED,
            font=("Segoe UI", 9),
            wraplength=170,
            justify="left"
        )
        self.sidebar_info.pack(anchor="w", padx=20)

        # Main content
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(main, bg=BG)
        topbar.pack(fill="x", padx=25, pady=(18, 18))

        search = tk.Entry(
            topbar,
            bg="#202830",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 11),
            width=42
        )
        search.insert(0, "Search or load an audio file…")
        search.pack(side="left", ipady=10, ipadx=10)
        search.bind("<Button-1>", lambda _event: self.load_audio())

        self.badge = tk.Label(
            topbar,
            text="●  Ready",
            bg=PANEL,
            fg=GREEN,
            font=("Segoe UI", 10),
            padx=14,
            pady=8
        )
        self.badge.pack(side="right")

        heading = tk.Frame(main, bg=BG)
        heading.pack(fill="x", padx=25, pady=(0, 17))

        tk.Label(
            heading,
            text="Digital Audio Equalizer",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        tk.Label(
            heading,
            text="Enhance your sound with FFT and FIR/IIR filters",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(5, 0))

        # Audio source, filter selection, and apply button
        top_cards = tk.Frame(main, bg=BG)
        top_cards.pack(fill="x", padx=25, pady=(0, 15))

        source = self.card(top_cards)
        source.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            source,
            text="AUDIO SOURCE",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=14, pady=(11, 5))

        source_row = tk.Frame(source, bg=PANEL)
        source_row.pack(fill="x", padx=12, pady=(0, 12))

        self.file_label = tk.Label(
            source_row,
            text="No audio selected",
            bg=DARK,
            fg=TEXT,
            anchor="w",
            padx=12,
            pady=12,
            font=("Segoe UI", 10)
        )
        self.file_label.pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )

        self.button(
            source_row, "Load Audio", self.load_audio
        ).pack(side="right")

        filters = self.card(top_cards, width=190)
        filters.pack(side="left", fill="y", padx=(0, 10))

        tk.Label(
            filters,
            text="FILTER TYPE",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=14, pady=(11, 5))

        self.filter_type = tk.StringVar(value="FIR")
        radio_row = tk.Frame(filters, bg=PANEL)
        radio_row.pack(fill="x", padx=8, pady=(2, 12))

        for value in ("FIR", "IIR"):
            tk.Radiobutton(
                radio_row,
                text=value,
                value=value,
                variable=self.filter_type,
                indicatoron=False,
                selectcolor="#123d2a",
                bg="#202830",
                fg=TEXT,
                activebackground="#123d2a",
                activeforeground=TEXT,
                relief="flat",
                bd=0,
                font=("Segoe UI", 10, "bold"),
                padx=14,
                pady=8
            ).pack(side="left", fill="x", expand=True, padx=3)

        apply_card = self.card(top_cards, width=205)
        apply_card.pack(side="right", fill="y")

        tk.Label(
            apply_card,
            text="READY TO PROCESS?",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(padx=12, pady=(12, 6))

        self.button(
            apply_card,
            "▶  Apply Equalizer",
            self.apply_equalizer,
            primary=True
        ).pack(fill="x", padx=12, pady=(0, 12))

        # Equalizer controls and visualization panel
        content = tk.Frame(main, bg=BG)
        content.pack(fill="both", expand=True, padx=25, pady=(0, 16))

        left = tk.Frame(content, bg=BG, width=410)
        left.pack(side="left", fill="y", padx=(0, 13))
        left.pack_propagate(False)

        controls = self.card(left)
        controls.pack(fill="x")

        tk.Label(
            controls,
            text="♫  Equalizer Controls",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=16, pady=(15, 4))

        tk.Label(
            controls,
            text="Adjust each frequency band's gain",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=16)

        self.bass = self.gain_control(
            controls, "Bass", "Below 250 Hz", "♬"
        )
        self.mid = self.gain_control(
            controls, "Mid", "250 Hz – 2 kHz", "∿"
        )
        self.treble = self.gain_control(
            controls, "Treble", "Above 2 kHz", "𝄞"
        )

        quick = self.card(left)
        quick.pack(fill="x", pady=(13, 0))

        tk.Label(
            quick,
            text="Quick Actions",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=15, pady=(13, 10))

        quick_row = tk.Frame(quick, bg=PANEL)
        quick_row.pack(fill="x", padx=10, pady=(0, 10))

        self.button(
            quick_row, "⌁  Waveform & FFT", self.show_graphs
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.button(
            quick_row, "↓  Save WAV", self.save_output
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.button(
            quick, "↺  Reset Gains", self.reset_gains
        ).pack(anchor="w", padx=10, pady=(0, 12))

        visual = self.card(content)
        visual.pack(side="left", fill="both", expand=True)

        visual_head = tk.Frame(visual, bg=PANEL)
        visual_head.pack(fill="x", padx=15, pady=(14, 8))

        tk.Label(
            visual_head,
            text="Waveform & FFT",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        tk.Label(
            visual_head,
            text="ORIGINAL / PROCESSED",
            bg=PANEL,
            fg=GREEN,
            font=("Segoe UI", 8, "bold")
        ).pack(side="right")

        self.graph_area = tk.Frame(visual, bg=DARK)
        self.graph_area.pack(
            fill="both", expand=True, padx=11, pady=(0, 10)
        )

        self.graph_placeholder = tk.Label(
            self.graph_area,
            text="Your audio visualizations will appear here",
            bg=DARK,
            fg=MUTED,
            font=("Segoe UI", 11)
        )
        self.graph_placeholder.pack(expand=True)

        tk.Label(
            visual,
            text="Apply the equalizer, then open the comparison plots.",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=15, pady=(0, 12))

        footer = tk.Frame(main, bg="#080b0e", height=38)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.status = tk.Label(
            footer,
            text="Ready — load a WAV or MP3 file to begin.",
            bg="#080b0e",
            fg=MUTED,
            anchor="w",
            font=("Segoe UI", 9)
        )
        self.status.pack(fill="both", padx=18)

    def nav_item(self, parent, icon, text, active=False, command=None):
        bg = "#123d2a" if active else SIDEBAR
        fg = TEXT if active else MUTED

        item = tk.Frame(parent, bg=bg, cursor="hand2")
        item.pack(fill="x", padx=11, pady=3)

        if active:
            tk.Frame(item, bg=GREEN, width=3).pack(
                side="left", fill="y"
            )

        tk.Label(
            item,
            text=icon,
            bg=bg,
            fg=GREEN if active else fg,
            font=("Segoe UI Symbol", 16),
            width=3
        ).pack(side="left", pady=9)

        label = tk.Label(
            item,
            text=text,
            bg=bg,
            fg=fg,
            font=("Segoe UI", 11)
        )
        label.pack(side="left", pady=9)

        if command:
            for widget in (item, label):
                widget.bind(
                    "<Button-1>",
                    lambda _event, fn=command: fn()
                )

    def gain_control(self, parent, name, description, icon):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=14, pady=(15, 3))

        tk.Label(
            row,
            text=icon,
            bg=PANEL,
            fg=GREEN,
            font=("Segoe UI Symbol", 18),
            width=2
        ).pack(side="left", padx=(0, 5))

        labels = tk.Frame(row, bg=PANEL, width=100)
        labels.pack(side="left")

        tk.Label(
            labels,
            text=name,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        tk.Label(
            labels,
            text=description,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(anchor="w")

        scale = tk.Scale(
            row,
            from_=-12,
            to=12,
            resolution=1,
            orient="horizontal",
            showvalue=False,
            bg=PANEL,
            fg=TEXT,
            troughcolor="#303940",
            activebackground=GREEN,
            highlightthickness=0,
            bd=0,
            sliderrelief="flat",
            length=125
        )
        scale.set(0)
        scale.pack(side="left", fill="x", expand=True, padx=4)

        value = tk.Label(
            row,
            text="0 dB",
            bg="#202830",
            fg=TEXT,
            width=7,
            font=("Segoe UI", 10, "bold"),
            pady=7
        )
        value.pack(side="right")

        scale.configure(
            command=lambda v, lbl=value: lbl.config(
                text=(
                    f"{int(float(v)):+d} dB"
                    if int(float(v))
                    else "0 dB"
                )
            )
        )
        return scale

    def focus_controls(self):
        self.bass.focus_set()
        self.status.config(
            text="Adjust the bass, midrange, and treble gains."
        )

    def load_audio(self):
        path = filedialog.askopenfilename(
            title="Select an audio file",
            filetypes=[
                ("Audio files", "*.wav *.mp3"),
                ("WAV audio", "*.wav"),
                ("MP3 audio", "*.mp3"),
                ("All files", "*.*"),
            ]
        )
        if not path:
            return

        try:
            self.audio_data = self.eq.load_audio(path)
            self.sample_rate = self.audio_data.sample_rate
            self.processed_audio = None
            self.file_path = path

            name = os.path.basename(path)
            self.file_label.config(text=name)
            self.sidebar_track.config(text=name)

            audio_format = os.path.splitext(path)[1][1:].upper() or "Audio"
            self.sidebar_info.config(
                text=f"{audio_format} audio  •  "
                     f"{self.sample_rate / 1000:.1f} kHz"
            )

            self.status.config(text=f"Loaded successfully: {name}")
            self.badge.config(text="●  Audio loaded", fg=GREEN)

            self.clear_graph()
        except Exception as error:
            messagebox.showerror("Audio Loading Error", str(error))

    def clear_graph(self):
        if self.plot_canvas is not None:
            self.plot_canvas.get_tk_widget().destroy()
            self.plot_canvas = None

        for widget in self.graph_area.winfo_children():
            widget.destroy()

        self.graph_placeholder = tk.Label(
            self.graph_area,
            text="Your audio visualizations will appear here",
            bg=DARK,
            fg=MUTED,
            font=("Segoe UI", 11)
        )
        self.graph_placeholder.pack(expand=True)

    def apply_equalizer(self):
        if self.audio_data is None:
            messagebox.showwarning(
                "No Audio",
                "Please load a WAV or MP3 file first."
            )
            return

        try:
            output, info = self.eq.process(
                self.audio_data.samples,
                self.sample_rate,
                bass_db=self.bass.get(),
                mid_db=self.mid.get(),
                treble_db=self.treble.get(),
                filter_type=self.filter_type.get(),
                normalize=False
            )
            self.processed_audio = output

            self.status.config(
                text=f"Processed with {info['filter_type']} filter • "
                     f"{info['processing_time_seconds']:.3f} seconds"
            )
            self.badge.config(text="●  Processed", fg=GREEN)

            # Refresh the embedded charts with the processed signal.
            self.show_graphs()
        except Exception as error:
            messagebox.showerror("Processing Error", str(error))

    def show_graphs(self):
        if self.audio_data is None:
            messagebox.showwarning(
                "No Audio",
                "Please load a WAV or MP3 file first."
            )
            return

        try:
            original = self.audio_data.samples
            processed = (
                self.processed_audio
                if self.processed_audio is not None
                else original
            )

            ot, ow = self.eq.waveform(original, self.sample_rate)
            pt, pw = self.eq.waveform(processed, self.sample_rate)
            of, om = self.eq.spectrum(original, self.sample_rate)
            pf, pm = self.eq.spectrum(processed, self.sample_rate)

            # Clear the old chart and remove the placeholder message.
            self.clear_graph()
            if self.graph_placeholder is not None:
                self.graph_placeholder.destroy()
                self.graph_placeholder = None

            fig = Figure(figsize=(8, 5.5), dpi=100, facecolor=BG)
            axes = fig.subplots(2, 2)

            plots = [
                (
                    axes[0, 0], ot[:2000], ow[:2000],
                    "Original Waveform", "Time (seconds)",
                    "Amplitude", GREEN
                ),
                (
                    axes[0, 1], pt[:2000], pw[:2000],
                    "Equalized Waveform", "Time (seconds)",
                    "Amplitude", PURPLE
                ),
                (
                    axes[1, 0], of, om,
                    "Original FFT", "Frequency (Hz)",
                    "Magnitude (dB)", GREEN
                ),
                (
                    axes[1, 1], pf, pm,
                    "Equalized FFT", "Frequency (Hz)",
                    "Magnitude (dB)", PURPLE
                ),
            ]

            for ax, x, y, title, xlabel, ylabel, color in plots:
                ax.set_facecolor(DARK)
                ax.plot(x, y, color=color, linewidth=0.85)
                ax.set_title(title, color=TEXT, pad=10)
                ax.set_xlabel(xlabel, color=MUTED, labelpad=7)
                ax.set_ylabel(ylabel, color=MUTED, labelpad=7)
                ax.tick_params(colors=MUTED)

                for spine in ax.spines.values():
                    spine.set_color(BORDER)

                ax.grid(True, color=BORDER, alpha=0.7)

            axes[1, 0].set_xlim(
                0, min(10000, self.sample_rate / 2)
            )
            axes[1, 1].set_xlim(
                0, min(10000, self.sample_rate / 2)
            )

            # Add vertical separation between rows to prevent label overlap.
            fig.subplots_adjust(
                left=0.12,
                right=0.98,
                bottom=0.13,
                top=0.94,
                wspace=0.42,
                hspace=0.78
            )

            self.plot_canvas = FigureCanvasTkAgg(
                fig, master=self.graph_area
            )
            self.plot_canvas.draw()
            self.plot_canvas.get_tk_widget().pack(
                fill="both", expand=True
            )

            self.status.config(text="Waveform and FFT displayed.")

        except Exception as error:
            messagebox.showerror("Graph Error", str(error))

    def save_output(self):
        if self.processed_audio is None:
            messagebox.showwarning(
                "No Processed Audio",
                "Apply the equalizer before saving."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Processed Audio",
            defaultextension=".wav",
            filetypes=[("WAV audio", "*.wav")]
        )
        if not path:
            return

        try:
            self.eq.save_audio(
                path,
                self.processed_audio,
                self.sample_rate
            )
            self.status.config(text=f"Output saved: {path}")
            messagebox.showinfo(
                "Saved", f"Processed audio saved to:\n{path}"
            )
        except Exception as error:
            messagebox.showerror("Saving Error", str(error))

    def reset_gains(self):
        self.bass.set(0)
        self.mid.set(0)
        self.treble.set(0)
        self.status.config(
            text="Gain controls reset to 0 dB. "
                 "Apply equalizer to process again."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEqualizerGUI(root)
    root.mainloop()