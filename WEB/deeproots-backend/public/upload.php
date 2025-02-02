<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['videoFile'])) {
    $uploadDir = "uploads/";
    $videoFile = $uploadDir . basename($_FILES["videoFile"]["name"]);
    
    // Save uploaded file
    if (move_uploaded_file($_FILES["videoFile"]["tmp_name"], $videoFile)) {
        $compressedFile = "videos/compressed.mp4";
        $courseName = htmlspecialchars($_POST["course"]);

        // Call Python script for compression
        $command = "python3 compress.py " . escapeshellarg($videoFile) . " " . escapeshellarg($compressedFile);
        shell_exec($command);

        // Add the course to index.html
        $indexFile = "index.html";
        $newCourse = '<div class="video-item" onclick="playVideo(\'videos/compressed.mp4\')">
                        <img src="thumbnail.jpg" alt="New Video">
                        <p>' . $courseName . '</p>
                      </div>';

        $content = file_get_contents($indexFile);
        $content = str_replace("<!-- Add new courses here -->", $newCourse . "\n<!-- Add new courses here -->", $content);
        file_put_contents($indexFile, $content);

        echo "Upload and compression successful!";
    } else {
        echo "File upload failed.";
    }
}
?>

