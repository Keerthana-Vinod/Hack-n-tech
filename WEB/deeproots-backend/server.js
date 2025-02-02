const express = require('express');
const multer = require('multer');
const path = require('path');
const { exec } = require('child_process');
const app = express();
const port = 3000;

// Serve static files (e.g., CSS, images, videos)
app.use(express.static(path.join(__dirname, 'public')));

// Route for root - Serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Set up file upload destination
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'public/videos');
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });

// Route for uploading the video
app.post('/upload', upload.single('videoFile'), (req, res) => {
    const uploadedVideoPath = req.file.path;
    const outputVideoPath = path.join('public/videos', 'compressed_' + req.file.filename);
    const pythonScriptPath = path.join(__dirname, 'compress_video.py');

    // Log the upload info
    console.log('File uploaded:', req.file);

    // Run Python script to compress video
    const command = `python3 ${pythonScriptPath} ${uploadedVideoPath} ${outputVideoPath}`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return res.status(500).send('Error during video compression.');
        }

        if (stderr) {
            console.error(`stderr: ${stderr}`);
        }

        console.log(`stdout: ${stdout}`);
        
        // Send success response with the output path
        res.send(`File uploaded and compressed successfully! <a href="/videos/${path.basename(outputVideoPath)}">Download Compressed Video</a>`);
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

