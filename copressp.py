import cv2
import numpy as np
import ffmpeg
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread

# Global variables to store file paths
input_video = None
output_video = None

# Function to compress video
def compress_video(input_video, output_video, threshold, progress_bar, status_label):
    cap = cv2.VideoCapture(input_video)

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Initialize FFmpeg writer
    process = (
        ffmpeg
        .input(input_video)  # Input video file for both video and audio
        .output(output_video, vcodec="libx264", crf=28, preset="slow", vsync="vfr", acodec='aac', audio_bitrate='128k')
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    # Read first frame
    ret, prev_frame = cap.read()
    if not ret:
        print("Error loading video.")
        cap.release()
        return

    # Convert first frame to grayscale
    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Write first frame to FFmpeg (video stream)
    process.stdin.write(prev_frame.tobytes())

    frame_index = 1  # Track frame progress

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray_prev, gray_curr)
        mean_diff = np.mean(diff)

        # Update progress bar
        progress = (frame_index / frame_count) * 100
        progress_bar['value'] = progress
        root.update_idletasks()  # Refresh the GUI

        # Print progress
        sys.stdout.write(f"\rProcessing frame {frame_index}/{frame_count} ({(frame_index/frame_count)*100:.2f}%)")
        sys.stdout.flush()

        # Only drop truly identical frames (low threshold)
        if mean_diff > threshold:
            process.stdin.write(frame.tobytes())  # Preserve video timing and audio
            gray_prev = gray_curr  # Update reference frame

        frame_index += 1

    # Clean up
    cap.release()
    process.stdin.close()
    process.wait()
    print("\nCompression complete! Output saved as", output_video)

    # Update status label
    status_label.config(text="Compression complete!")
    messagebox.showinfo("Success", f"Compression complete! Output saved as {output_video}")

# Function to handle file selection and compression
def start_compression():
    global input_video, output_video

    if not input_video:
        messagebox.showerror("Error", "Please select an input video file.")
        return

    if not output_video:
        messagebox.showerror("Error", "Please select an output video file.")
        return

    threshold = float(threshold_entry.get())

    # Reset progress bar and status label
    progress_bar['value'] = 0
    status_label.config(text="Compressing...")

    # Run compression in a separate thread to avoid freezing the GUI
    compression_thread = Thread(target=compress_video, args=(input_video, output_video, threshold, progress_bar, status_label))
    compression_thread.start()

# Function to select input video
def select_input_video():
    global input_video
    input_video = filedialog.askopenfilename(title="Select Input Video", filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
    if input_video:
        input_label.config(text=f"Input: {input_video}")

# Function to select output video
def select_output_video():
    global output_video
    output_video = filedialog.asksaveasfilename(title="Save Compressed Video As", defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4")])
    if output_video:
        output_label.config(text=f"Output: {output_video}")

# Create the main GUI window
root = tk.Tk()
root.title("Video Compressor")

# Input file selection button
input_label = tk.Label(root, text="Select Input Video:")
input_label.grid(row=0, column=0, padx=10, pady=10)
input_button = tk.Button(root, text="Browse", command=select_input_video)
input_button.grid(row=0, column=1, padx=10, pady=10)

# Output file selection button
output_label = tk.Label(root, text="Save Compressed Video As:")
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
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Status label
status_label = tk.Label(root, text="", fg="blue")
status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Start compression button
compress_button = tk.Button(root, text="Compress Video", command=start_compression)
compress_button.grid(row=5, column=0, columnspan=2, padx=10, pady=20)

# Run the GUI
root.mainloop()
