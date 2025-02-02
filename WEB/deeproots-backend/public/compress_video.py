import cv2
import numpy as np
import ffmpeg
import sys

if len(sys.argv) != 3:
    print("Usage: python3 compress.py input.mp4 output.mp4")
    sys.exit(1)

input_video = sys.argv[1]
output_video = sys.argv[2]

cap = cv2.VideoCapture(input_video)
fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# FFmpeg process
process = (
    ffmpeg
    .input(input_video)
    .output(output_video, vcodec="libx264", crf=28, preset="slow", acodec='aac', audio_bitrate='128k')
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

ret, prev_frame = cap.read()
if not ret:
    print("Error loading video.")
    cap.release()
    sys.exit(1)

gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
process.stdin.write(prev_frame.tobytes())

frame_index = 1
threshold = 2.0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray_prev, gray_curr)
    mean_diff = np.mean(diff)

    sys.stdout.write(f"\rProcessing frame {frame_index}/{frame_count} ({(frame_index/frame_count)*100:.2f}%)")
    sys.stdout.flush()

    if mean_diff > threshold:
        process.stdin.write(frame.tobytes())
        gray_prev = gray_curr

    frame_index += 1

cap.release()
process.stdin.close()
process.wait()
print("\nCompression complete! Output saved as", output_video)

