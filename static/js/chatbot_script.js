// Chatbot Logic
const chatbotToggle = document.getElementById('chatbot-toggle'); 
const chatbotWindow = document.getElementById('chatbot-window'); 
const chatInput = document.getElementById('chat-input'); 
const chatSend = document.getElementById('chat-send'); 
const chatMessages = document.getElementById('chat-messages'); 
const toggleIcon = chatbotToggle.querySelector('i');

let isOpen = false;

// Toggle Chatbot Window 
chatbotToggle.addEventListener('click', () => { 
    isOpen = !isOpen; 
    if (isOpen) { 
        chatbotWindow.classList.remove('d-none'); 
        chatbotWindow.classList.add('d-flex');
        chatbotToggle.innerHTML = `<i data-lucide="x" width="24" height="24"></i>`;                 // Change icon to X
    } 
    else { 
        chatbotWindow.classList.remove('d-flex'); 
        chatbotWindow.classList.add('d-none'); 
        chatbotToggle.innerHTML = `<i data-lucide="message-circle" width="24" height="24"></i>`;    // Change icon to message-circle
    }
    lucide.createIcons(); // Refresh icons 
});

// Send Message Logic 
async function handleSend() { 
    const questionText = chatInput.value.trim(); 
    if (!questionText) return;
    // Add User Message
    appendMessage(questionText, 'user');
    chatInput.value = '';

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Fetch response from chatbot endpoint
    const response = await fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: questionText })
    });

    if (response.ok) {
        const data = await response.json();
        // Groq gives output in markdown format so we clean the data using DOMPurify and Marked
        const rawMarkdown = data.response;
        const safeHTML = DOMPurify.sanitize(marked.parse(rawMarkdown));

        // Add Bot Reply
        appendMessage(safeHTML, 'bot');
    }
    else {
        appendMessage("Sorry, There seems to be a problem with the chatbot. Please Try again.", "bot");
    }
    // Scroll to Bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Append Message to UI 
function appendMessage(text, type) { 
    const msgDiv = document.createElement('div'); 
    msgDiv.className = `d-flex mb-3 ${type === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
    const bubble = document.createElement('div');
    bubble.className = `p-3 rounded-4 ${type === 'user' ? 'bg-success text-white rounded-bottom-right-0' : 'bg-white border text-dark rounded-bottom-left-0'}`;
    bubble.style.maxWidth = '85%';

    const p = document.createElement('p');
    p.className = 'mb-0 small';
    p.innerHTML = text;

    bubble.appendChild(p);
    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);
}

// Event Listeners for Sending 
chatSend.addEventListener('click', handleSend); 
chatInput.addEventListener('keypress', (e) => { 
    if (e.key === 'Enter') handleSend(); 
});

lucide.createIcons();