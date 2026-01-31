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
    // Start processing immediately
    socket.emit('process_file', {});
    updateOverlay("Connecting to secure vault...", 10);
});

socket.on('status', function(data) {
    // Update the main UI indicator
    updateStatus(data.message, data.icon);

    // Update the full-screen overlay if still processing
    if (isProcessing) {
        updateOverlay(data.message, 50); // Default jump

        if(data.message.includes("Vector")) updateOverlay(data.message, 70);
        if(data.message.includes("Finalizing")) updateOverlay(data.message, 90);
        if(data.message.includes("Loading")) updateOverlay(data.message, 40);
    }
});

socket.on('ready', function(data) {
    // 1. Finish the progress bar
    updateOverlay("Analysis Complete", 100);

    // 2. Short delay to show 100%, then hide overlay
    setTimeout(() => {
        // Fade out overlay
        overlay.style.transition = 'opacity 0.5s ease';
        overlay.style.opacity = '0';
        setTimeout(() => {
            overlay.classList.add('d-none');

            // 3. Enable Inputs
            isProcessing = false;
            inputField.disabled = false;
            sendBtn.disabled = false;
            inputField.placeholder = `Ask about your ${window.currentFile.type.toUpperCase()}...`;
            inputField.focus();

            // 4. Add "I am ready" system message
            const welcomeMsg = `<strong>System Ready.</strong><br>I have processed <em>${window.currentFile.name}</em>. You can now ask questions about its content.`;
            addMessageToHistory(welcomeMsg, 'assistant');

            // Show preview if exists (CSV)
            if (data.preview) {
                showDataPreview(data.preview);
            }
        }, 500);
    }, 800);

    updateStatus('Ready', '✅');
});

socket.on('stream_start', function() {
    isStreaming = true;
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

    // Format sources nicely
    let sourceHtml = '';
    if (data.sources) {
        // Convert plain text sources to HTML with styling
        sourceHtml = data.sources.replace(/\n/g, '<br>');
    }

    // Delay to allow DOM update
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