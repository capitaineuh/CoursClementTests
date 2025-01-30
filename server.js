require('dotenv').config();
const express = require('express');
const axios = require('axios');
const path = require('path');
const cookieParser = require('cookie-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Variables d'environnement pour éviter d'exposer les clés API (.env)
const API_KEY = process.env.OPENAI_API_KEY;

// Contenu par défaut du message système
let systemMessageContent = "Vous êtes un assistant très serviable";

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

/**
 * Réinitialise les cookies de l'utilisateur.
 */
app.post('/api/reset-cookies', (req, res) => {
    res.clearCookie('chatHistory');
    res.send('Cookies reset');
});

/**
 * Met à jour le message système en fonction du mode sélectionné.
 */
app.post('/api/update-system-message', (req, res) => {
    const mode = req.body.mode;
    const modes = {
        'Mode 1': "Mode 1: commence automatiquement la réponse par 'mode 1:' ",
        'Mode 2': "Mode JeunePoèteDeLaRue: Parle moi comme un rappeur technique. commence automatiquement la réponse par 'mode 2:'",
        'Mode 3': "Mode 2: commence automatiquement la réponse par 'mode 3:'"
    };

    if (modes[mode]) {
        systemMessageContent = modes[mode];
        res.send('System message updated');
    } else {
        console.error(`Invalid mode: ${mode}`);
        res.status(400).send('Invalid mode');
    }
});

/**
 * Gère la conversation avec l'API OpenAI.
 */
app.post('/api/chat', async (req, res) => {
    const prompt = req.body.prompt;
    console.log('Received prompt:', prompt);

    const chatHistory = getChatHistory(req);
    chatHistory.push({ role: "user", content: prompt });

    const messages = [
        { role: "system", content: systemMessageContent },
        ...chatHistory
    ];

    try {
        const reply = await fetchChatReply(messages);
        chatHistory.push({ role: "assistant", content: reply });

        res.cookie('chatHistory', JSON.stringify(chatHistory), { httpOnly: true });
        res.json({ reply });
    } catch (error) {
        console.error('Error fetching response from OpenAI:', error.message);
        res.status(500).send('Error communicating with OpenAI');
    }
});

/**
 * Récupère l'historique du chat à partir des cookies.
 */
function getChatHistory(req) {
    return req.cookies.chatHistory ? JSON.parse(req.cookies.chatHistory) : [];
}

/**
 * Envoie les messages à l'API OpenAI et récupère la réponse.
 */
async function fetchChatReply(messages) {
    const response = await axios.post('https://api.openai.com/v1/chat/completions', {
        model: "gpt-3.5-turbo",
        messages: messages
    }, {
        headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json'
        }
    });
    return response.data.choices[0].message.content;
}

// Démarrer le serveur
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});