const uploadButton = document.getElementById("upload-button");
const imageUpload = document.getElementById("image-upload");
const resultSection = document.getElementById("result");
const uploadedImage = document.getElementById("uploaded-image");
const description = document.getElementById("description");

uploadButton.addEventListener("click", async () => {
    const file = imageUpload.files[0];
    if (!file) {
        alert("Please select an image!");
        return;
    }

    const formData = new FormData();
    formData.append("image", file);

    try {
        const response = await fetch("https://your-backend.onrender.com/upload", {
            method: "POST",
            body: formData,
        });
        const data = await response.json();

        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }

        // Display results
        uploadedImage.src = data.url;
        description.textContent = data.description;
        resultSection.classList.remove("hidden");
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while uploading.");
    }
});