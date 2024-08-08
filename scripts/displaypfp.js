function displayImage() {
    const imageInput = document.getElementById('pfp-upload');
    const imageDisplay = document.getElementById('imageDisplay');
    const file = imageInput.files[0]; // Get the selected file

    if (file) {
        const reader = new FileReader();

        // Set up the onload event to display the image
        reader.onload = function(e) {
            imageDisplay.src = e.target.result; // Set the image source to the file's data URL
            imageDisplay.style.display = 'block'; // Make sure the image is visible
        };

        // Read the file as a data URL
        reader.readAsDataURL(file);
    }
}