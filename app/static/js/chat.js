const socket = io();
let isStreaming = false;
let isProcessing = true; // Start in processing mode

const overlay = document.getElementById('processing-overlay');
const statusText = document.getElementById('overlay-status');
const progressBar = document.getElementById('loading-bar');
const inputField = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

socket.on('connect', function() {
    console.log('Connected to server');
    socket.emit('process_file', {});
    updateOverlay("Connecting to secure vault...", 10);
});

socket.on('status', function(data) {
    updateStatus(data.message, data.icon);
    if (isProcessing) {
        updateOverlay(data.message, 50);
        if(data.message.includes("Vector")) updateOverlay(data.message, 70);
        if(data.message.includes("Finalizing")) updateOverlay(data.message, 90);
        if(data.message.includes("Loading")) updateOverlay(data.message, 40);
    }
});

socket.on('ready', function(data) {
    updateOverlay("Analysis Complete", 100);
    setTimeout(() => {
        overlay.style.transition = 'opacity 0.5s ease';
        overlay.style.opacity = '0';
        setTimeout(() => {
            overlay.classList.add('d-none');
            isProcessing = false;
            inputField.disabled = false;
            sendBtn.disabled = false;
            inputField.placeholder = "Ask about your documents...";
            inputField.focus();

            const welcomeMsg = `<strong>System Ready.</strong><br>I have synchronized your vault with the uploaded documents. You can now query across all of them.`;
            addMessageToHistory(welcomeMsg, 'assistant');

            if (data.preview) {
                showDataPreview(data.preview);
            }
        }, 500);
    }, 800);
    updateStatus('Ready', '✅');
});

// --- HANDLE THINKING & INDEXING STEPS ---
socket.on('process_status', function(data) {
    let processContainer = document.getElementById('current-process-container');

    // Create container if it doesn't exist
    if (!processContainer || data.step === 'thinking') {
        processContainer = createProcessBubble();
    }

    const contentDiv = processContainer.querySelector('.process-content');

    if (data.step === 'thinking') {
        contentDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="pulse-ring me-2"></span>
                <span class="text-muted">${data.message}</span>
            </div>`;
    }
    else if (data.step === 'indexing') {
        let cardsHtml = `<div class="mb-2"><small class="text-success fw-bold">${data.message}</small></div>`;
        cardsHtml += `<div class="d-flex gap-2 overflow-auto pb-2" style="white-space: nowrap; scrollbar-width: thin;">`;

        if (data.data) {
            data.data.forEach(item => {
                cardsHtml += `
                    <div class="index-card p-2 rounded bg-dark border border-secondary" style="min-width: 200px; max-width: 200px; white-space: normal;">
                        <div class="d-flex justify-content-between mb-1">
                            <span class="badge bg-secondary" style="font-size: 0.6rem">Ref #${item.id}</span>
                            <span class="text-muted" style="font-size: 0.55rem; overflow: hidden; text-overflow: ellipsis;">${item.page}</span>
                        </div>
                        <div style="font-size: 0.7rem; color: #a0aec0; height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                            "${item.content}"
                        </div>
                    </div>`;
            });
        }
        cardsHtml += `</div>`;
        contentDiv.innerHTML = cardsHtml;
    }
    scrollToBottom();
});

socket.on('stream_start', function() {
    isStreaming = true;

    // 1. Finalize the thought bubble by removing its dynamic ID
    const processContainer = document.getElementById('current-process-container');
    if(processContainer) {
        processContainer.id = '';
    }

    // 2. IMPORTANT: Move the streaming div to the bottom of the container
    const container = document.getElementById('chat-container');
    const streamingDiv = document.getElementById('streaming-message');
    container.appendChild(streamingDiv); // This physically moves it after the user's question

    streamingDiv.classList.remove('d-none');
    document.getElementById('stream-content').innerHTML = '<span class="streaming-cursor">▋</span>';
    scrollToBottom();
});

socket.on('stream_chunk', function(data) {
    const content = document.getElementById('stream-content');
    const chunkText = typeof data === 'string' ? data : (data.chunk || '');

    const currentHtml = content.innerHTML.replace('<span class="streaming-cursor">▋</span>', '');
    content.innerHTML = currentHtml + chunkText + '<span class="streaming-cursor">▋</span>';

    scrollToBottom();
});

socket.on('stream_end', function(data) {
    isStreaming = false;
    const content = document.getElementById('stream-content');
    content.innerHTML = content.innerHTML.replace('<span class="streaming-cursor">▋</span>', '');

    let sourceHtml = '';
    if (data && data.sources) {
        sourceHtml = data.sources.replace(/\n/g, '<br>');
    }

    setTimeout(() => {
        const finalContent = content.innerHTML + (sourceHtml ? `<div class="mt-2 pt-2 border-top border-secondary small text-muted">${sourceHtml}</div>` : '');
        addMessageToHistory(finalContent, 'assistant');

        document.getElementById('streaming-message').classList.add('d-none');
        document.getElementById('stream-content').innerHTML = '';
    }, 100);
});

socket.on('response', function(data) {
    addMessageToHistory(data.content, data.role);
});

socket.on('error', function(data) {
    alert('Vault Error: ' + data.message);
    isStreaming = false;
    updateStatus('Error occurred', '⚠️');
});

// --- FORM SUBMISSION ---
document.getElementById('chat-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const message = inputField.value.trim();

    if (!message || isStreaming || isProcessing) return;

    addMessageToHistory(message, 'user');
    inputField.value = '';

    socket.emit('chat_message', {message: message});
    updateStatus('Thinking...', '🤔');
});

// --- UI HELPERS ---

function updateOverlay(text, percent) {
    statusText.textContent = text;
    progressBar.style.width = percent + '%';
}

function addMessageToHistory(content, role) {
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.className = `message mb-3 ${role === 'user' ? 'text-end' : ''}`;

    const bubble = document.createElement('div');
    bubble.className = `d-inline-block p-3 rounded-3 message-bubble ${role === 'user' ? 'user-bubble' : 'ai-bubble'}`;
    bubble.style.maxWidth = '85%';
    bubble.innerHTML = content;

    div.appendChild(bubble);
    container.appendChild(div);
    scrollToBottom();
}

function createProcessBubble() {
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.id = 'current-process-container';
    div.className = 'message mb-2';
    div.innerHTML = `
        <div class="d-inline-block p-3 rounded-3" style="background: rgba(30, 41, 59, 0.4); border: 1px dashed #4a5568; max-width: 85%; width: fit-content;">
            <div class="process-content"></div>
        </div>
    `;
    container.appendChild(div);
    return div;
}

function updateStatus(message, icon) {
    const el = document.getElementById('status-indicator');
    el.style.opacity = '0';
    setTimeout(() => {
        el.textContent = `${icon} ${message}`;
        el.style.opacity = '1';
    }, 200);
}

function scrollToBottom() {
    const container = document.getElementById('chat-container');
    container.scrollTop = container.scrollHeight;
}

function showDataPreview(html) {
    const container = document.getElementById('chat-container');
    const div = document.createElement('div');
    div.className = 'message mb-3';
    div.innerHTML = `
        <div class="d-inline-block p-3 rounded-3 ai-bubble w-100">
            <strong>📊 Data Preview</strong>
            <div class="overflow-auto mt-2">${html}</div>
        </div>`;
    container.appendChild(div);
    scrollToBottom();
}