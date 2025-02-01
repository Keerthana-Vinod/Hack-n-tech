import cv2
import numpy as np
import ffmpeg
import sys

# Load video
input_video = "input.mp4"
output_video = "compressed.mp4"
cap = cv2.VideoCapture(input_video)

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Initialize FFmpeg writer (preserves sync and includes audio)
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
    exit()

# Convert first frame to grayscale
gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

# Write first frame to FFmpeg (video stream)
process.stdin.write(prev_frame.tobytes())

frame_index = 1  # Track frame progress
threshold = 2.0  # Lower threshold = less skipping, preserves sync better

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray_prev, gray_curr)
    mean_diff = np.mean(diff)

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

