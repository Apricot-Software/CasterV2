function sendPost() {
    const postContent = document.getElementById('post-input').innerText;
    const sendButton = document.getElementById('sendButton');
    sendButton.className = "positiveButtonDisabled";
    sendButton.setAttribute("disabled", "");

    if (postContent === '') {
        alert('Post content cannot be empty.');
        sendButton.className = "positiveButton";
        sendButton.removeAttribute("disabled");
        return;
    }

    fetch('/api/sendpost', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: postContent })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.postId) {
            window.location.href = `/post?id=${data.postId}`;
        } else {
            console.error('Post ID not found in response');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

document.getElementById('post-input').addEventListener('paste', function(event) {
    event.preventDefault();

    // Get the pasted content from clipboard
    const clipboardData = event.clipboardData || window.clipboardData;
    let pastedData = clipboardData.getData('text');

    // Optionally, you can use HTML if you want to keep plain text and remove HTML formatting
    // let pastedData = clipboardData.getData('text/html') || clipboardData.getData('text');

    // Insert the cleaned text
    document.execCommand('insertHTML', false, pastedData);
});