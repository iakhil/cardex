const uploadButton = document.getElementById("upload-button");
const imageUpload = document.getElementById("image-upload");
const resultSection = document.getElementById("result");
const uploadedImage = document.getElementById("uploaded-image");
const apiResponse = document.getElementById("api-response");

uploadButton.addEventListener("click", async () => {
    const file = imageUpload.files[0];
    if (!file) {
        alert("Please select an image!");
        return;
    }

    const formData = new FormData();
    formData.append("image", file);

    try {
        const response = await fetch("http://127.0.0.1:5000/upload", { // Use localhost for testing
            method: "POST",
            body: formData,
        });
        const data = await response.json();

        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }

        // Display results verbatim
        apiResponse.textContent = data.description;
        uploadedImage.src = data.url;
        resultSection.classList.remove("hidden");
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while uploading.");
    }
});
