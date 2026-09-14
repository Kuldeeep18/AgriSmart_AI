// Chatbot Logic
const chatbotToggle = document.getElementById('chatbot-toggle'); 
const chatbotWindow = document.getElementById('chatbot-window'); 
const chatbotCloseBtn = document.getElementById('chatbot-close-btn');
const chatInput = document.getElementById('chat-input'); 
const chatSend = document.getElementById('chat-send'); 
const chatMessages = document.getElementById('chat-messages'); 

let isOpen = false;

function openChatbot() {
    isOpen = true;
    chatbotWindow.classList.remove('hidden');
    chatbotWindow.classList.add('flex');
    chatbotToggle.innerHTML = `<i data-lucide="x" class="w-6 h-6"></i>`;
    if (typeof lucide !== 'undefined') lucide.createIcons();
    chatInput?.focus();
}

function closeChatbot() {
    isOpen = false;
    chatbotWindow.classList.remove('flex');
    chatbotWindow.classList.add('hidden');
    chatbotToggle.innerHTML = `<i data-lucide="sparkles" class="w-6 h-6 group-hover:rotate-12 transition-transform"></i>`;
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

// Toggle Chatbot Window 
chatbotToggle?.addEventListener('click', () => { 
    if (isOpen) {
        closeChatbot();
    } else {
        openChatbot();
    }
});

chatbotCloseBtn?.addEventListener('click', () => {
    closeChatbot();
});

// Append Message to UI 
function appendMessage(text, type) { 
    const msgDiv = document.createElement('div'); 
    msgDiv.className = `flex items-end gap-2 max-w-full min-w-0 ${type === 'user' ? 'justify-end' : 'justify-start'}`;
    
    if (type === 'user') {
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble-content bg-primary text-white p-3 rounded-2xl rounded-br-none max-w-[85%] text-sm leading-relaxed shadow-sm min-w-0 break-words';
        bubble.innerHTML = text;
        msgDiv.appendChild(bubble);
    } else {
        const iconDiv = document.createElement('div');
        iconDiv.className = 'w-7 h-7 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0';
        iconDiv.innerHTML = '<i data-lucide="bot" class="w-3.5 h-3.5 text-emerald-600"></i>';
        
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble-content bg-white border border-gray-100 shadow-sm p-3 rounded-2xl rounded-bl-none max-w-[85%] text-sm text-gray-700 leading-relaxed min-w-0 break-words';
        bubble.innerHTML = text;
        
        msgDiv.appendChild(iconDiv);
        msgDiv.appendChild(bubble);
    }

    chatMessages.appendChild(msgDiv);
    if (typeof lucide !== 'undefined') lucide.createIcons();
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show Typing Indicator
function showTypingIndicator() {
    const indicatorDiv = document.createElement('div');
    indicatorDiv.id = 'bot-typing-indicator';
    indicatorDiv.className = 'flex items-end gap-2 justify-start max-w-full min-w-0';
    indicatorDiv.innerHTML = `
        <div class="w-7 h-7 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
            <i data-lucide="bot" class="w-3.5 h-3.5 text-emerald-600"></i>
        </div>
        <div class="bg-white border border-gray-100 shadow-sm px-4 py-3 rounded-2xl rounded-bl-none max-w-[85%] text-sm text-gray-400 flex items-center gap-1.5">
            <span class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></span>
            <span class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.2s]"></span>
            <span class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.4s]"></span>
        </div>
    `;
    chatMessages.appendChild(indicatorDiv);
    if (typeof lucide !== 'undefined') lucide.createIcons();
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide Typing Indicator
function hideTypingIndicator() {
    const indicator = document.getElementById('bot-typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Send Message Logic 
async function handleSend() { 
    const questionText = chatInput.value.trim(); 
    if (!questionText) return;

    // Add User Message (escaped plain text)
    const userMessageDiv = document.createElement('div');
    userMessageDiv.textContent = questionText;
    appendMessage(userMessageDiv.innerHTML, 'user');
    chatInput.value = '';

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Show Typing Indicator
    showTypingIndicator();

    try {
        // Fetch response from chatbot endpoint
        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: questionText })
        });

        hideTypingIndicator();

        if (response.ok) {
            const data = await response.json();
            const rawMarkdown = data.response || "No response received.";
            let safeHTML = rawMarkdown;
            if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
                safeHTML = marked.parse(rawMarkdown);
            }
            if (typeof DOMPurify !== 'undefined') {
                safeHTML = DOMPurify.sanitize(safeHTML);
            }

            // Add Bot Reply
            appendMessage(safeHTML, 'bot');
        } else {
            appendMessage("Sorry, there seems to be a problem reaching BioGrow AI. Please try again.", "bot");
        }
    } catch (err) {
        hideTypingIndicator();
        appendMessage("Network connection error. Please check your connection and try again.", "bot");
    }

    // Scroll to Bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Event Listeners for Sending 
chatSend?.addEventListener('click', handleSend); 
chatInput?.addEventListener('keypress', (e) => { 
    if (e.key === 'Enter') handleSend(); 
});

if (typeof lucide !== 'undefined') lucide.createIcons();