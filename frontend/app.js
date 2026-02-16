const API_BASE = 'http://127.0.0.1:8000';

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const chatMessages = document.getElementById('chatMessages');
const queryInput = document.getElementById('queryInput');
const sendButton = document.getElementById('sendButton');
const clearChatBtn = document.getElementById('clearChat');
const exportChatBtn = document.getElementById('exportChat');
const documentsList = document.getElementById('documentsList');
const chatStatus = document.getElementById('chatStatus');
const charCounter = document.getElementById('charCounter');
const suggestedQuestions = document.getElementById('suggestedQuestions');
const suggestedChips = document.getElementById('suggestedChips');
const citationModal = document.getElementById('citationModal');

let documentsUploaded = false;
let uploadedDocuments = [];
let chatHistory = [];

// ===== TOAST NOTIFICATION SYSTEM =====
function showToast(title, message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>',
        error: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
        warning: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type]}</div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== FILE TYPE ICONS =====
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
        pdf: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><path d="M9 15h4"></path></svg>',
        txt: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><line x1="10" y1="9" x2="8" y2="9"></line></svg>',
        md: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>'
    };
    return icons[ext] || icons.txt;
}

// ===== CHARACTER COUNTER =====
queryInput.addEventListener('input', () => {
    const length = queryInput.value.length;
    charCounter.textContent = `${length} / 500`;
    
    if (length > 450) {
        charCounter.style.color = 'var(--error)';
    } else if (length > 400) {
        charCounter.style.color = 'var(--warning)';
    } else {
        charCounter.style.color = 'var(--text-secondary)';
    }
});

// ===== UPLOAD FUNCTIONALITY =====
uploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

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

async function handleFiles(files) {
    if (files.length === 0) return;

    // Validate file sizes
    for (let file of files) {
        if (file.size > 25 * 1024 * 1024) {
            showToast('Upload Failed', `${file.name} exceeds 25MB limit`, 'error');
            return;
        }
    }

    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    uploadStatus.innerHTML = '<div class="status-item processing">⏳ Processing files...</div>';

    try {
        const startTime = Date.now();
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        const uploadTime = ((Date.now() - startTime) / 1000).toFixed(1);

        if (response.ok) {
            uploadStatus.innerHTML = `<div class="status-item success">✓ Processed in ${uploadTime}s</div>`;
            showToast('Upload Successful', `${result.processed} file(s) processed successfully`, 'success');
            
            // Add documents to list
            Array.from(files).forEach((file) => {
                addDocumentCard(file);
            });

            documentsUploaded = true;
            queryInput.disabled = false;
            sendButton.disabled = false;
            chatStatus.textContent = `${uploadedDocuments.length} document(s) loaded`;

            // Clear welcome message
            if (chatMessages.querySelector('.welcome-message')) {
                chatMessages.innerHTML = '';
            }

            // Generate suggested questions
            generateSuggestedQuestions();

            setTimeout(() => {
                uploadStatus.innerHTML = '';
            }, 3000);
        } else {
            uploadStatus.innerHTML = `<div class="status-item error">✗ ${result.detail}</div>`;
            showToast('Upload Failed', result.detail, 'error');
        }
    } catch (error) {
        uploadStatus.innerHTML = '<div class="status-item error">✗ Connection error</div>';
        showToast('Connection Error', 'Failed to connect to server', 'error');
    }
}

// ===== DOCUMENT CARD MANAGEMENT =====
function addDocumentCard(file) {
    if (documentsList.querySelector('.empty-state')) {
        documentsList.innerHTML = '';
    }

    const sizeKB = (file.size / 1024).toFixed(2);
    const timestamp = new Date().toLocaleString();
    const docId = Date.now() + Math.random();

    const docCard = document.createElement('div');
    docCard.className = 'document-card active';
    docCard.dataset.id = docId;
    docCard.innerHTML = `
        <div class="doc-header">
            <div class="doc-name">
                <span class="doc-icon">${getFileIcon(file.name)}</span>
                ${file.name}
            </div>
            <div class="doc-badge">Active</div>
        </div>
        <div class="doc-meta">
            <div class="meta-item">
                <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="9" y1="9" x2="15" y2="9"></line>
                    <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
                <span>Chunks: --</span>
            </div>
            <div class="meta-item">
                <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                    <polyline points="13 2 13 9 20 9"></polyline>
                </svg>
                <span>${sizeKB} KB</span>
            </div>
        </div>
        <div class="doc-timestamp">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            ${timestamp}
        </div>
        <div class="doc-actions">
            <button class="btn-small" onclick="viewDocument('${docId}')">View</button>
            <button class="btn-small danger" onclick="removeDocument('${docId}')">Remove</button>
        </div>
    `;

    documentsList.appendChild(docCard);
    uploadedDocuments.push({ id: docId, name: file.name, file });
}

window.removeDocument = function(docId) {
    const card = document.querySelector(`[data-id="${docId}"]`);
    if (card) {
        card.remove();
        uploadedDocuments = uploadedDocuments.filter(doc => doc.id !== docId);
        showToast('Document Removed', 'Document deleted successfully', 'success');

        if (uploadedDocuments.length === 0) {
            documentsList.innerHTML = '<div class="empty-state"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg><p>No documents uploaded yet</p></div>';
            documentsUploaded = false;
            queryInput.disabled = true;
            sendButton.disabled = true;
            chatStatus.textContent = 'No documents loaded';
            suggestedQuestions.style.display = 'none';
        } else {
            chatStatus.textContent = `${uploadedDocuments.length} document(s) loaded`;
        }
    }
};

window.viewDocument = function(docId) {
    const doc = uploadedDocuments.find(d => d.id === docId);
    if (doc) {
        showToast('Document Info', `${doc.name} - ${(doc.file.size / 1024).toFixed(2)} KB`, 'success');
    }
};

// ===== SUGGESTED QUESTIONS =====
function generateSuggestedQuestions() {
    const questions = [
        "Summarize the main points",
        "What are the key findings?",
        "Explain the main concepts",
        "What conclusions are drawn?",
        "List the important details"
    ];

    suggestedChips.innerHTML = '';
    questions.slice(0, 3).forEach(q => {
        const chip = document.createElement('div');
        chip.className = 'suggested-chip';
        chip.textContent = q;
        chip.onclick = () => {
            queryInput.value = q;
            sendQuery();
        };
        suggestedChips.appendChild(chip);
    });

    suggestedQuestions.style.display = 'block';
}

// ===== CLEAR CHAT =====
clearChatBtn.addEventListener('click', () => {
    chatMessages.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
            </div>
            <h2>Chat cleared!</h2>
            <p>Start asking questions about your documents</p>
        </div>
    `;
    chatHistory = [];
    showToast('Chat Cleared', 'Conversation history cleared', 'success');
});

// ===== EXPORT CHAT =====
exportChatBtn.addEventListener('click', () => {
    if (chatHistory.length === 0) {
        showToast('Export Failed', 'No messages to export', 'warning');
        return;
    }

    let exportText = `DocuMind Chat Export\n`;
    exportText += `Exported: ${new Date().toLocaleString()}\n`;
    exportText += `Total Messages: ${chatHistory.length}\n`;
    exportText += `\n${'='.repeat(60)}\n\n`;

    chatHistory.forEach((msg, idx) => {
        exportText += `[${msg.time}] ${msg.role === 'user' ? 'You' : 'DocuMind'}:\n`;
        exportText += `${msg.content}\n\n`;
        if (msg.sources && msg.sources.length > 0) {
            exportText += `Sources:\n`;
            msg.sources.forEach((src, i) => {
                exportText += `  ${i + 1}. ${src.source_file} (Chunk ${src.chunk_index})\n`;
            });
            exportText += `\n`;
        }
        exportText += `${'-'.repeat(60)}\n\n`;
    });

    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `documind-chat-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('Export Successful', 'Chat history exported', 'success');
});

// ===== SEND QUERY =====
sendButton.addEventListener('click', sendQuery);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !sendButton.disabled) {
        sendQuery();
    }
});

async function sendQuery() {
    const query = queryInput.value.trim();
    if (!query) return;

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Add to history
    chatHistory.push({ role: 'user', content: query, time: timestamp });

    // Add user message
    addMessage('user', query, timestamp);
    queryInput.value = '';
    charCounter.textContent = '0 / 500';
    sendButton.disabled = true;

    // Add loading message
    const loadingId = Date.now();
    addLoadingMessage(loadingId);

    const startTime = Date.now();

    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: 3
            })
        });

        const result = await response.json();
        const responseTime = ((Date.now() - startTime) / 1000).toFixed(1);

        // Remove loading message
        document.getElementById(`msg-${loadingId}`)?.remove();

        if (response.ok) {
            const msgTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            // Add to history
            chatHistory.push({ 
                role: 'assistant', 
                content: result.answer, 
                time: msgTimestamp,
                sources: result.sources,
                responseTime: responseTime
            });

            addMessage('assistant', result.answer, msgTimestamp, result.sources, responseTime);
        } else {
            addMessage('assistant', `⚠️ Error: ${result.detail}`, new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        }
    } catch (error) {
        document.getElementById(`msg-${loadingId}`)?.remove();
        addMessage('assistant', '⚠️ Connection error. Please try again.', new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        showToast('Connection Error', 'Failed to get response', 'error');
    }

    sendButton.disabled = false;
}

// ===== ADD MESSAGE =====
function addMessage(role, content, timestamp, sources = null, responseTime = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatarIcon = role === 'user' 
        ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
        : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>';

    let sourcesHTML = '';
    if (sources && sources.length > 0) {
        sourcesHTML = '<div class="message-sources"><strong>Sources:</strong>';
        sources.forEach((source, idx) => {
            sourcesHTML += `<div class="source-item" onclick="showCitation('${source.source_file}', '${source.text}', ${source.chunk_index})">${idx + 1}. ${source.source_file} (Chunk ${source.chunk_index})</div>`;
        });
        sourcesHTML += '</div>';
    }

    const copyBtnHTML = role === 'assistant' 
        ? `<button class="copy-btn" onclick="copyMessage(this, '${content.replace(/'/g, "\\'")}')">
               <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                   <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                   <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
               </svg>
               Copy
           </button>` 
        : '';

    const responseTimeHTML = responseTime ? `<span class="response-time">⚡ ${responseTime}s</span>` : '';

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatarIcon}</div>
        <div class="message-wrapper">
            <div class="message-content">${content}${sourcesHTML}</div>
            <div class="message-actions">
                <span class="message-time">${timestamp}</span>
                ${responseTimeHTML}
                ${copyBtnHTML}
            </div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addLoadingMessage(id) {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading-message';
    loadingDiv.id = `msg-${id}`;

    loadingDiv.innerHTML = `
        <div class="message-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
        </div>
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    `;

    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ===== COPY MESSAGE =====
window.copyMessage = async function(button, text) {
    try {
        await navigator.clipboard.writeText(text);
        button.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Copied!
        `;
        setTimeout(() => {
            button.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                Copy
            `;
        }, 2000);
        showToast('Copied!', 'Message copied to clipboard', 'success');
    } catch (err) {
        showToast('Copy Failed', 'Could not copy message', 'error');
    }
};

// ===== CITATION MODAL =====
window.showCitation = function(filename, text, chunkIndex) {
    document.querySelector('.citation-source').textContent = `${filename} - Chunk ${chunkIndex}`;
    document.querySelector('.citation-text').textContent = text;
    citationModal.classList.add('active');
};

window.closeCitationModal = function() {
    citationModal.classList.remove('active');
};

// Close modal on outside click
citationModal.addEventListener('click', (e) => {
    if (e.target === citationModal) {
        closeCitationModal();
    }
});

// ===== EXAMPLE QUESTION CLICKS =====
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('example-chip')) {
        queryInput.value = e.target.textContent.replace(/"/g, '');
        if (!queryInput.disabled) {
            sendQuery();
        }
    }
});
