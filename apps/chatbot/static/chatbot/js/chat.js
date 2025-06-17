document.addEventListener('DOMContentLoaded', function() {
  // Chat elements
  const chatWidget = document.getElementById('chat-widget');
  const chatToggle = document.getElementById('chat-toggle');
  const chatClose = document.getElementById('chat-close');
  const chatInput = document.getElementById('chat-input');
  const chatSend = document.getElementById('chat-send');
  const chatMessages = document.getElementById('chat-messages');
  
  // Toggle chat open/close
  chatToggle.addEventListener('click', function() {
    // Toggle visibility classes
    if (chatWidget.classList.contains('opacity-0')) {
      // Opening chat
      chatWidget.classList.remove('opacity-0', 'translate-y-5', 'pointer-events-none');
      chatWidget.classList.add('opacity-100', 'translate-y-0');
      chatToggle.querySelector('.open-icon').classList.add('hidden');
      chatToggle.querySelector('.close-icon').classList.remove('hidden');
      
      // Focus input field
      chatInput.focus();
      // Scroll to bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } else {
      // Closing chat
      chatWidget.classList.add('opacity-0', 'translate-y-5', 'pointer-events-none');
      chatWidget.classList.remove('opacity-100', 'translate-y-0');
      chatToggle.querySelector('.open-icon').classList.remove('hidden');
      chatToggle.querySelector('.close-icon').classList.add('hidden');
    }
  });
  
  // Close chat
  chatClose.addEventListener('click', function() {
    chatWidget.classList.add('opacity-0', 'translate-y-5', 'pointer-events-none');
    chatWidget.classList.remove('opacity-100', 'translate-y-0');
    chatToggle.querySelector('.open-icon').classList.remove('hidden');
    chatToggle.querySelector('.close-icon').classList.add('hidden');
  });
  
  // Send message on button click
  chatSend.addEventListener('click', sendMessage);
  
  // Send message on Enter key
  chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
  
  // Function to send a message
  function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage('user', message);
    
    // Clear input
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Send to server
    fetch('/chat/message/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
      // Hide typing indicator
      hideTypingIndicator();
      
      // Use the addMessage function to display the bot's response
      addMessage('bot', data.response, true); // <--- MODIFIED HERE

    })
    .catch(error => {
      hideTypingIndicator();
      addMessage('bot', 'Sorry, something went wrong. Please try again.', false); // <--- MODIFIED HERE
      console.error('Error:', error);
    });
  }
  
  // Add a message to the chat with typing effect and correct styling
  function addMessage(type, text, isTyping = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageWrapper = document.createElement('div'); // Renamed from messageDiv for clarity

    // Apply common and type-specific wrapper classes based on widget.html structure
    messageWrapper.className = `chat-message ${type} max-w-[80%]`; // Common class
    if (type === 'user') {
        messageWrapper.classList.add('self-end'); // Align user messages to the right
    } else {
        messageWrapper.classList.add('self-start'); // Align bot messages to the left
    }

    const messageContent = document.createElement('div');
    // Apply common and type-specific content bubble classes based on widget.html structure
    messageContent.className = 'px-4 py-2 rounded-2xl shadow-sm'; // Common classes
    if (type === 'user') {
        messageContent.classList.add('bg-pink-500', 'text-white', 'rounded-br-sm'); // User bubble style
    } else {
        messageContent.classList.add('bg-gray-100', 'text-gray-800', 'rounded-bl-sm'); // Bot bubble style
    }

    if (type === 'bot' && isTyping) {
        // Apply typing effect for bot messages
        messageContent.innerHTML = ''; // Start empty
        messageWrapper.appendChild(messageContent); // Append content bubble to wrapper
        chatMessages.appendChild(messageWrapper); // Append wrapper to chat area
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll down

        let i = 0;
        const speed = 30; // milliseconds per character

        function typeWriter() {
            if (i < text.length) {
                // Handle potential HTML entities correctly if needed
                // Append character by character
                messageContent.innerHTML += text.charAt(i);
                i++;
                chatMessages.scrollTop = chatMessages.scrollHeight; // Keep scrolled down
                setTimeout(typeWriter, speed);
            }
        }
        typeWriter();

    } else {
        // For user messages or non-typing bot messages, display immediately
        // Use innerText for user messages to prevent HTML injection
        // Use innerHTML for bot messages if they might contain formatting (like from formatMessage)
        if (type === 'user') {
             messageContent.innerText = text;
        } else {
             // If your bot messages might contain HTML (e.g., from formatMessage), use innerHTML
             // Otherwise, innerText is safer. Let's assume potential HTML for now.
             messageContent.innerHTML = formatMessage(text); // Apply formatting if needed
        }
        messageWrapper.appendChild(messageContent); // Append content bubble to wrapper
        chatMessages.appendChild(messageWrapper); // Append wrapper to chat area
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll down
    }
  }
  
  // Format message with code blocks and tables
  function formatMessage(text) {
    // Handle code blocks
    text = text.replace(/```(sql)?\n([\s\S]*?)\n```/g, '<div class="bg-gray-900 text-gray-100 p-2 rounded text-xs font-mono overflow-x-auto">$2</div>');
    
    // Handle tables (pre-formatted text)
    if (text.includes('\n') && (text.includes('|') || text.includes('-+-'))) {
      return `<div class="font-mono text-xs whitespace-pre overflow-x-auto">${text}</div>`;
    }
    
    // Handle line breaks
    return text.replace(/\n/g, '<br>');
  }
  
  // Show typing indicator
  function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message bot self-start max-w-[80%]';
    typingDiv.id = 'typing-indicator';
    
    const bubble = document.createElement('div');
    bubble.className = 'bg-gray-100 text-gray-800 px-4 py-2 rounded-2xl rounded-bl-sm shadow-sm flex';
    
    const dots = document.createElement('div');
    dots.className = 'flex items-center';
    
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement('div');
      dot.className = 'w-2 h-2 bg-gray-400 rounded-full mx-0.5 animate-bounce';
      dot.style.animationDelay = `${i * 0.2}s`;
      dots.appendChild(dot);
    }
    
    bubble.appendChild(dots);
    typingDiv.appendChild(bubble);
    chatMessages.appendChild(typingDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  // Hide typing indicator
  function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
});