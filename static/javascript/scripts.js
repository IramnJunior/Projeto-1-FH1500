const chats = [
    {name: "Chat 1", messages: []}
];

let currentChat = 0;

const chatList = document.getElementById('chats');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const addChatButton = document.getElementById('add-chat-button');
const typingIndicator = document.getElementById('typing-indicator');

addChatButton.addEventListener('click', () => {
    const newChatName = prompt("Digite o nome do novo chat:");
    if (newChatName) {
        chats.push({ name: newChatName, messages: [] });
        updateChatList();
        currentChat = chats.length - 1;
        displayChat();
    }
});

function displayChat() {
    const chat = chats[currentChat];
    chatMessages.innerHTML = '';

    chat.messages.forEach(message => {
        if (message.role == 'user') {
            const userMessageElement = document.createElement('div');
            userMessageElement.classList.add('message', 'user');
            userMessageElement.innerHTML = marked.parse(message.parts[0]);
            chatMessages.appendChild(userMessageElement);
        } else if (message.role == 'model') {
            const botMessageElement = document.createElement('div');
            botMessageElement.classList.add('message', 'bot');
            botMessageElement.innerHTML = marked.parse(message.parts[0]);
            chatMessages.appendChild(botMessageElement);
        }
    });
}

function updateChatList() {
    chatList.innerHTML = '';
    chats.forEach((chat, index) => {
        const chatListItem = document.createElement('li');
        chatListItem.textContent = chat.name;
        chatListItem.addEventListener('click', () => {
            currentChat = index;
            displayChat();
        });
        chatList.appendChild(chatListItem);
    });
}

function sendMessage() {
    const message = messageInput.value;
    if (message.trim()) {
        messageInput.value = '';
        chats[currentChat].messages.push({'role': 'user', 'parts': [`${message}`]});
    
        const userMessageElement = document.createElement('div');
        userMessageElement.classList.add('message', 'user');
        userMessageElement.innerHTML = message;

        chatMessages.appendChild(userMessageElement);

        axios.post('/send-response', {history: chats[currentChat].messages})
        .then(response => {
            const botResponse = response.data;
            console.log("Pergunta recebida");

            chats[currentChat].messages.push({'role': 'model', 'parts': [`${botResponse}`]});
             
            const botMessageElement = document.createElement('div');
            botMessageElement.classList.add('message', 'bot');
            botMessageElement.innerHTML = marked.parse(botResponse);

            chatMessages.appendChild(botMessageElement)
            


            const chat_name = chats[currentChat].name
            const history_chat = chats[currentChat].messages
            console.log(chat_name)
            console.log(history_chat)


            axios.post('/send-chats', {chat_name: chat_name, chat_history: history_chat})  
        })
        .then(error => {
            console.log(error)
        })
    }
}

function get_chat_history() {
    axios.get("/get-chat-history")
    .then(response => {
        const chat_history = response.data
        console.log(chat_history) 
    })
    .then(error => {
        console.log(error)
    })
}

get_chat_history();

updateChatList();
displayChat();

sendButton.addEventListener('click', sendMessage);
