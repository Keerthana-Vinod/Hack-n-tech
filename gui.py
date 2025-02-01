import cv2
import numpy as np
import ffmpeg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import os
from PIL import Image, ImageTk

# Global variables
input_video = None
output_video = None
progress_value = 0  # Used to track progress

# Function to compress video
def compress_video(threshold):
    global progress_value

    if not input_video or not output_video:
        messagebox.showerror("Error", "Please select both input and output video files.")
        return

    cap = cv2.VideoCapture(input_video)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_count == 0:
        messagebox.showerror("Error", "Invalid video file or cannot read frames.")
        cap.release()
        return

    # Open FFmpeg process
    process = (
        ffmpeg
        .input(input_video)
        .output(output_video, vcodec="libx264", crf=28, preset="slow", acodec="aac", audio_bitrate="128k")
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    # Read first frame
    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        process.stdin.close()
        process.wait()
        messagebox.showerror("Error", "Could not read first frame.")
        return

    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    process.stdin.write(prev_frame.tobytes())  # Write first frame

    frame_index = 1

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray_prev, gray_curr)
        mean_diff = np.mean(diff)

        if mean_diff > threshold:
            process.stdin.write(frame.tobytes())
            gray_prev = gray_curr  # Update previous frame

        # Update progress bar every 10 frames
        if frame_index % 10 == 0:
            progress_value = int((frame_index / frame_count) * 100)
            root.after(1, update_progress_bar)

        frame_index += 1

    cap.release()
    process.stdin.close()
    process.wait()

    root.after(1, lambda: status_label.config(text="Compression Complete!"))
    messagebox.showinfo("Success", f"Compression complete! Output saved as {output_video}")

# Function to update progress bar
def update_progress_bar():
    progress_bar["value"] = progress_value

# Function to start compression in a separate thread
def start_compression():
    try:
        threshold = float(threshold_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid numeric threshold.")
        return

    status_label.config(text="Compressing...")
    progress_bar["value"] = 0  # Reset progress bar

    # Run compression in a separate thread to keep UI responsive
    compression_thread = Thread(target=compress_video, args=(threshold,))
    compression_thread.start()

# Function to select input video
def select_input_video():
    global input_video
    input_video = filedialog.askopenfilename(title="Select Input Video", filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
    if input_video:
        input_label.config(text=f"Input: {os.path.basename(input_video)}")

# Function to select output video
def select_output_video():
    global output_video
    output_video = filedialog.asksaveasfilename(title="Save Compressed Video As", defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4")])
    if output_video:
        output_label.config(text=f"Output: {os.path.basename(output_video)}")

# Create GUI window
root = tk.Tk()
root.title("Video Compressor")

# Set the favicon (if exists)
try:
    if os.path.exists("favicon.png"):
        icon = ImageTk.PhotoImage(Image.open("favicon.png"))
        root.iconphoto(False, icon)
except Exception as e:
    print(f"Error loading favicon: {e}")

# Input selection
input_label = tk.Label(root, text="Input: Not selected")
input_label.grid(row=0, column=0, padx=10, pady=10)
input_button = tk.Button(root, text="Browse", command=select_input_video)
input_button.grid(row=0, column=1, padx=10, pady=10)

# Output selection
output_label = tk.Label(root, text="Output: Not selected")
output_label.grid(row=1, column=0, padx=10, pady=10)
output_button = tk.Button(root, text="Browse", command=select_output_video)
output_button.grid(row=1, column=1, padx=10, pady=10)

# Threshold input
threshold_label = tk.Label(root, text="Threshold (for frame difference):")
threshold_label.grid(row=2, column=0, padx=10, pady=10)
threshold_entry = tk.Entry(root)
threshold_entry.insert(0, "2.0")  # Default threshold
threshold_entry.grid(row=2, column=1, padx=10, pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", maximum=100)
progress_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Status label
status_label = tk.Label(root, text="", fg="blue")
status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Start compression button
compress_button = tk.Button(root, text="Compress Video", command=start_compression)
compress_button.grid(row=5, column=0, columnspan=2, padx=10, pady=20)

# Run GUI
root.mainloop()

