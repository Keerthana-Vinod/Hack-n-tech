#include <stdio.h>
#include <stdlib.h>
#include <opencv2/opencv.hpp>

#define CHANGE_THRESHOLD 15  

using namespace cv;

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <input_video> <output_video>\n", argv[0]);
        return -1;
    }

    char *input_video = argv[1];
    char *output_video = argv[2];
    char temp_video[] = "temp.avi";

    VideoCapture cap(input_video);
    if (!cap.isOpened()) {
        printf("Error: Cannot open video file %s\n", input_video);
        return -1;
    }

    int width = cap.get(CAP_PROP_FRAME_WIDTH);
    int height = cap.get(CAP_PROP_FRAME_HEIGHT);
    int fps = cap.get(CAP_PROP_FPS);

    VideoWriter writer(temp_video, VideoWriter::fourcc('X', 'V', 'I', 'D'), fps, Size(width, height));

    Mat prev_frame, curr_frame, diff_frame;
    
    // Read first frame
    if (!cap.read(prev_frame)) {
        printf("Error: Cannot read first frame\n");
        return -1;
    }
    
    cvtColor(prev_frame, prev_frame, COLOR_BGR2GRAY); // Convert to grayscale
    writer.write(prev_frame);

    while (cap.read(curr_frame)) {
        cvtColor(curr_frame, curr_frame, COLOR_BGR2GRAY); // Convert to grayscale

        absdiff(prev_frame, curr_frame, diff_frame);
        int nonZeroCount = countNonZero(diff_frame);

        if (nonZeroCount > CHANGE_THRESHOLD * width * height / 100) {
            writer.write(curr_frame);
            prev_frame = curr_frame.clone(); // Update reference frame
        }
    }

    cap.release();
    writer.release();

    // Compress using FFmpeg
    char ffmpeg_cmd[512];
    snprintf(ffmpeg_cmd, sizeof(ffmpeg_cmd),
             "ffmpeg -i temp.avi -vcodec libx264 -crf 28 -preset slow -y %s", output_video);
    system(ffmpeg_cmd);

    printf("Compression complete! Output saved as %s\n", output_video);
    return 0;
}

