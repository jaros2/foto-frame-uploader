document.getElementById('uploadBtn').addEventListener('click', () => {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    
    if (files.length === 0) {
        alert('Please select files to upload.');
        return;
    }
    
    // Determine job name from URL path
    let path = window.location.pathname.replace(/^\/|\/$/g, '');
    let jobName = path ? path : 'default';
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    const xhr = new XMLHttpRequest();
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('statusText');
    const uploadBtn = document.getElementById('uploadBtn');
    
    uploadBtn.disabled = true;
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';
    statusText.innerText = 'Uploading...';
    
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.style.width = percentComplete + '%';
        }
    });
    
    xhr.onload = () => {
        uploadBtn.disabled = false;
        if (xhr.status === 200) {
            statusText.innerText = 'Upload complete! Processing in background.';
            statusText.style.color = 'green';
            fileInput.value = ''; // clear selection
        } else {
            statusText.innerText = 'Upload failed. Error ' + xhr.status;
            statusText.style.color = 'red';
        }
    };
    
    xhr.onerror = () => {
        uploadBtn.disabled = false;
        statusText.innerText = 'An error occurred during the upload.';
        statusText.style.color = 'red';
    };
    
    xhr.open('POST', `/upload/${jobName}`, true);
    xhr.send(formData);
});
