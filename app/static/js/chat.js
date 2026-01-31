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
            inputField.placeholder = `Ask about your ${window.currentFile.type.toUpperCase()}...`;
            inputField.focus();

            const welcomeMsg = `<strong>System Ready.</strong><br>I have processed <em>${window.currentFile.name}</em>. You can now ask questions about its content.`;
            addMessageToHistory(welcomeMsg, 'assistant');

            if (data.preview) {
                showDataPreview(data.preview);
            }
        }, 500);
    }, 800);
    updateStatus('Ready', '✅');
});

// --- UPDATED PROCESS HANDLER ---
socket.on('process_status', function(data) {
    let processContainer = document.getElementById('current-process-container');

    // Create container if it doesn't exist (start of thinking)
    if (!processContainer || data.step === 'thinking') {
        processContainer = createProcessBubble();
    }

    const contentDiv = processContainer.querySelector('.process-content');

    if (data.step === 'thinking') {
        contentDiv.innerHTML = `<div class="d-flex align-items-center"><span class="pulse-ring me-2"></span> <span class="text-muted">${data.message}</span></div>`;
    }
    else if (data.step === 'indexing') {
        // Show the cards
        let cardsHtml = `<div class="mb-2"><small class="text-success fw-bold">${data.message}</small></div>`;
        cardsHtml += `<div class="d-flex gap-2 overflow-auto pb-2" style="white-space: nowrap; scrollbar-width: thin;">`;

        if (data.data) {
            data.data.forEach(item => {
                cardsHtml += `
                    <div class="index-card p-2 rounded bg-dark border border-secondary" style="min-width: 200px; max-width: 200px; white-space: normal;">
                        <div class="d-flex justify-content-between mb-1">
                            <span class="badge bg-secondary" style="font-size: 0.6rem">Ref #${item.id}</span>
                            <span class="text-muted" style="font-size: 0.6rem">Pg ${item.page}</span>
                        </div>
                        <div style="font-size: 0.7rem; color: #a0aec0; height: 40px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">"${item.content}"</div>
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

    // Remove ID so this process container becomes "history"
    const processContainer = document.getElementById('current-process-container');
    if(processContainer) processContainer.id = '';

    document.getElementById('streaming-message').classList.remove('d-none');
    document.getElementById('stream-content').innerHTML = '<span class="streaming-cursor">▋</span>';
    document.getElementById('stream-sources').innerHTML = '';
    scrollToBottom();
});

socket.on('stream_chunk', function(data) {
    const content = document.getElementById('stream-content');
    const cleanContent = content.innerHTML.replace('<span class="streaming-cursor">▋</span>', '');
    content.innerHTML = cleanContent + data.chunk + '<span class="streaming-cursor">▋</span>';
    scrollToBottom();
});

socket.on('stream_end', function(data) {
    isStreaming = false;
    const content = document.getElementById('stream-content');
    content.innerHTML = content.innerHTML.replace('<span class="streaming-cursor">▋</span>', '');

    let sourceHtml = '';
    if (data.sources) {
        sourceHtml = data.sources.replace(/\n/g, '<br>');
    }

    setTimeout(() => {
        addMessageToHistory(content.innerHTML + (sourceHtml ? `<div class="mt-2 pt-2 border-top border-secondary small text-muted">${sourceHtml}</div>` : ''), 'assistant');
        document.getElementById('streaming-message').classList.add('d-none');
        document.getElementById('stream-content').innerHTML = '';
    }, 100);
});

socket.on('response', function(data) {
    addMessageToHistory(data.content, data.role);
});

socket.on('error', function(data) {
    alert('Error: ' + data.message);
    isStreaming = false;
    updateStatus('Error occurred', '⚠️');
});

document.getElementById('chat-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const message = inputField.value.trim();

    if (!message || isStreaming || isProcessing) return;

    addMessageToHistory(message, 'user');
    inputField.value = '';

    socket.emit('chat_message', {message: message});
    updateStatus('Thinking...', '🤔');
});

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
    // Styled for "System thought"
    div.innerHTML = `
        <div class="d-inline-block p-3 rounded-3" style="background: rgba(30, 41, 59, 0.5); border: 1px dashed #4a5568; max-width: 85%; width: fit-content;">
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
    container.insertBefore(div, container.firstChild);
}