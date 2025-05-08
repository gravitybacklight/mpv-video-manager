#!/usr/bin/env python3
from guizero import App, ListBox, PushButton, Text, Box, Slider
from tkinter import Frame, filedialog
from mpv import MPV
import os
from send2trash import send2trash
import shutil


class MPVBrowserApp:
    def __init__(self):
        self.app = App("MPV Manager", width=800, height=600, layout="grid")
        self.folder_path = ""
        self.video_files = []
        self.current_video_index = None
        self.move_path = ""

        # UI Layout

        # Create embedded frame for MPV
        self.video_frame = Frame(self.app.tk, width=480, height=360, bg="black")
        self.video_frame.grid(row=0, column=0, padx=10, pady=10)

        self.video_listbox = ListBox(
            self.app,
            items=[],
            width=290,
            height=360,
            command=self.on_listbox_select,
            grid=[1, 0],
        )

        self.controls_box = Box(self.app, grid=[0, 1])
        self.progress_slider = Slider(self.controls_box, start=0, end=100, width="fill")
        self.prev_button = PushButton(
            self.controls_box,
            text="\u23ee Prev",
            command=self.play_prev_video,
            width=10,
            align="left",
        )
        self.play_button = PushButton(
            self.controls_box,
            text="\u25b6 Play",
            command=self.play_selected_video,
            width=10,
            align="left",
        )
        self.stop_button = PushButton(
            self.controls_box,
            text="\u23f9 Stop",
            command=self.stop_selected_video,
            width=10,
            align="left",
        )
        self.next_button = PushButton(
            self.controls_box,
            text="\u23ed Next",
            command=self.play_next_video,
            width=10,
            align="left",
        )

        self.delete_box = Box(self.app, grid=[0, 2])
        self.delete_button = PushButton(
            self.delete_box,
            text="\U0001f5d1 Delete",
            command=self.delete_current_video,
            align="left",
        )
        self.move_button = PushButton(
            self.delete_box,
            text="\U00002722 Move",
            command=self.move_current_video,
            align="left",
        )

        self.select_button = PushButton(
            self.app,
            text="Select Play Folder",
            command=self.select_folder,
            grid=[1, 1],
            width=33,
        )
        self.select_move_button = PushButton(
            self.app,
            text="Select Move Folder",
            command=self.move_folder,
            grid=[1, 2],
            width=33,
        )

        self.now_playing = Text(
            self.app, text="Now Playing: -", grid=[0, 3, 1, 1], height=5
        )

        self.player = MPV(
            wid=str(self.video_frame.winfo_id()),
            input_default_bindings=True,
            input_vo_keyboard=True,
        )
        self.player.observe_property("duration", self.on_duration)
        self.player.observe_property("time-pos", self.on_time_pos)
        self.app.when_key_pressed = self.key_handler

        self.app.tk.after(200, self.setup_embed)

    def setup_embed(self):
        self.player.wid = str(self.video_frame.winfo_id())

    def key_handler(self, key):
        keysym = key.tk_event.keysym
        if keysym == "Delete":
            self.delete_current_video()
        elif keysym == "Left":
            self.play_prev_video()
        elif keysym == "Right":
            self.play_next_video()
        elif keysym == "m" or keysym == "M":
            self.move_current_video()

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        self.select_button.text = f"Select Play Folder ({self.folder_path})"
        self.load_video_files()

    def move_folder(self):
        self.move_path = filedialog.askdirectory()
        self.select_move_button.text = f"Select Move Folder ({self.move_path})"

    def load_video_files(self):
        if not self.folder_path:
            return
        video_extensions = (".mp4", ".avi", ".mov", ".mkv", ".webm")
        self.video_files = [
            f
            for f in os.listdir(self.folder_path)
            if f.lower().endswith(video_extensions)
        ]
        self.video_listbox.clear()
        for video in self.video_files:
            self.video_listbox.append(video)

    def play_selected_video(self):
        selected = self.video_listbox.value
        if selected:
            self.play_video(selected)

    def stop_selected_video(self):
        self.player.stop()

    def play_video(self, filename):
        filepath = os.path.join(self.folder_path, filename)
        self.player.play(filepath)
        self.current_video_index = self.video_files.index(filename)
        self.video_listbox.value = filename
        self.now_playing.value = f"Now Playing: {filename}"

    def play_next_video(self):
        if (
            self.current_video_index is not None
            and self.current_video_index < len(self.video_files) - 1
        ):
            next_index = self.current_video_index + 1
            self.play_video(self.video_files[next_index])

    def play_prev_video(self):
        if self.current_video_index is not None and self.current_video_index > 0:
            prev_index = self.current_video_index - 1
            self.play_video(self.video_files[prev_index])

    def delete_current_video(self):
        if self.current_video_index is not None:
            current_file = self.video_files[self.current_video_index]
            file_path = os.path.join(self.folder_path, current_file)
            self.player.stop()
            self.now_playing.value = "Now Playing: -"
            try:
                send2trash(file_path)
                self.video_files.pop(self.current_video_index)
                self.video_listbox.remove(current_file)
                new_current_file = self.video_files[self.current_video_index]
                self.play_video(new_current_file)
            except Exception as e:
                print(f"Error deleting file: {e}")

    def move_current_video(self):
        if self.current_video_index is not None and self.move_path != "":
            current_file = self.video_files[self.current_video_index]
            file_path = os.path.join(self.folder_path, current_file)
            self.player.stop()
            self.now_playing.value = "Now Playing: -"
            try:
                shutil.move(file_path, os.path.join(self.move_path, current_file))
                self.video_files.pop(self.current_video_index)
                self.video_listbox.remove(current_file)
                new_current_file = self.video_files[self.current_video_index]
                self.play_video(new_current_file)
            except Exception as e:
                print(f"Error moving file: {e}")

    def on_listbox_select(self, filename):
        # Store current index for navigation
        self.current_video_index = self.video_files.index(filename)

    def run(self):
        self.app.display()

    def on_duration(self, name, value):
        if value:
            self.video_duration = value
            self.progress_slider.end = value
            if self.current_video_index is not None:
                filename = self.video_files[self.current_video_index]
                formatted = self.format_duration(value)
                self.now_playing.value = f"Now Playing: {filename} ({formatted})"

    def on_time_pos(self, name, value):
        if value is not None:
            self.progress_slider.value = value

    def format_duration(self, seconds):
        if seconds is None:
            return "--:--"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02}"


if __name__ == "__main__":
    MPVBrowserApp().run()
