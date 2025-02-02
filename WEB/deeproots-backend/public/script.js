// Hardcoded credentials
const users = {
    "faculty": "password123", // Faculty user
    "student": "studentpass"  // Student user (no upload access)
};

// Login function
function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    if (users[username] && users[username] === password) {
        localStorage.setItem("loggedInUser", username);
        document.getElementById("loginForm").style.display = "none";
        document.getElementById("logoutBtn").style.display = "block";

        if (username === "faculty") {
            document.getElementById("facultyUpload").style.display = "block";
        }

        document.getElementById("loginMessage").textContent = `Welcome, ${username}!`;
    } else {
        document.getElementById("loginMessage").textContent = "Invalid credentials.";
    }
}

// Logout function
function logout() {
    localStorage.removeItem("loggedInUser");
    document.getElementById("loginForm").style.display = "block";
    document.getElementById("logoutBtn").style.display = "none";
    document.getElementById("facultyUpload").style.display = "none";
    document.getElementById("loginMessage").textContent = "";
}

// Load user on page refresh
window.onload = function () {
    let savedUser = localStorage.getItem("loggedInUser");
    if (savedUser) {
        document.getElementById("loginForm").style.display = "none";
        document.getElementById("logoutBtn").style.display = "block";
        if (savedUser === "faculty") {
            document.getElementById("facultyUpload").style.display = "block";
        }
        document.getElementById("loginMessage").textContent = `Welcome, ${savedUser}!`;
    }
};

// Dummy upload function
function uploadVideo() {
    let fileInput = document.getElementById("fileUpload");
    if (fileInput.files.length > 0) {
        document.getElementById("uploadMessage").textContent = "Upload successful!";
    } else {
        document.getElementById("uploadMessage").textContent = "Please select a file.";
    }
}

