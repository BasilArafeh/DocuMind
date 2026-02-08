const API_BASE = 'http://127.0.0.1:8000';

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const chatMessages = document.getElementById('chatMessages');
const queryInput = document.getElementById('queryInput');
const sendButton = document.getElementById('sendButton');

let documentsUploaded = false;

// Upload Area Click
uploadArea.addEventListener('click', () => fileInput.click());

// File Input Change
fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragging');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragging');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragging');
    handleFiles(e.dataTransfer.files);
});

// Handle File Upload
async function handleFiles(files) {
    if (files.length === 0) return;

    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    uploadStatus.innerHTML = '<div class="status-item">Uploading files...</div>';

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            uploadStatus.innerHTML = `
                <div class="status-item success">
                    ✅ ${result.message}
                </div>
            `;
            documentsUploaded = true;
            enableChat();
        } else {
            uploadStatus.innerHTML = `
                <div class="status-item error">
                    ❌ Upload failed: ${result.detail || 'Unknown error'}
                </div>
            `;
        }
    } catch (error) {
        uploadStatus.innerHTML = `
            <div class="status-item error">
                ❌ Error: ${error.message}
            </div>
        `;
    }
}

// Enable Chat
function enableChat() {
    queryInput.disabled = false;
    sendButton.disabled = false;
    queryInput.placeholder = 'Ask me anything about your documents...';
}

// Send Query
sendButton.addEventListener('click', sendQuery);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !sendButton.disabled) {
        sendQuery();
    }
});

async function sendQuery() {
    const query = queryInput.value.trim();
    if (!query) return;

    // Add user message
    addMessage(query, 'user');
    queryInput.value = '';

    // Show loading
    const loadingId = addMessage('Thinking<span class="loading"></span>', 'assistant', true);

    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, top_k: 3 })
        });

        const result = await response.json();

        // Remove loading message
        document.getElementById(loadingId).remove();

        if (response.ok) {
            addMessage(result.answer, 'assistant', false, result.sources);
        } else {
            addMessage(`Error: ${result.detail || 'Unknown error'}`, 'assistant');
        }
    } catch (error) {
        document.getElementById(loadingId).remove();
        addMessage(`Error: ${error.message}`, 'assistant');
    }
}

// Add Message to Chat
function addMessage(content, sender, isLoading = false, sources = null) {
    const messageId = `msg-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.id = messageId;

    let sourcesHTML = '';
    if (sources && sources.length > 0) {
        sourcesHTML = '<div class="message-sources"><strong>📚 Sources:</strong>';
        sources.forEach((source, index) => {
            sourcesHTML += `<div class="source-item">${index + 1}. ${source.source_file} (chunk ${source.chunk_index})</div>`;
        });
        sourcesHTML += '</div>';
    }

    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
        ${sourcesHTML}
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageId;
}
