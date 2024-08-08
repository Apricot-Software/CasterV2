function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


async function uploadSettings() {
    const saveButton = document.getElementById('saveButton');
    saveButton.className = "positiveButtonDisabled";
    saveButton.setAttribute("disabled", "");

    const bioInput = document.getElementById('bioInput').value;
    const displayNameInput = document.getElementById('displayName').value;
    const fileInput = document.getElementById('pfp-upload');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('file', file);

    try {
        const fileResponse = await fetch('/api/uploadpfp', {
            method: 'POST',
            body: formData
        });
        if (!fileResponse.ok) throw new Error('File upload failed');

        const displayNameResponse = await fetch('/api/updatedisplayname', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: displayNameInput })
        });
        if (!displayNameResponse.ok) throw new Error('Display name update failed');

        const bioResponse = await fetch('/api/updatebio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: bioInput })
        });
        if (!bioResponse.ok) throw new Error('Bio update failed');

    } catch (error) {
        console.error('Error:', error);
    }

    await sleep(2000);
    window.location.href = '/profile';

    // Re-enable the save button after the sleep delay
    saveButton.className = "positiveButton";
    saveButton.removeAttribute("disabled");
}