from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import asyncio

app = FastAPI()

# Configurações e Estado do GB Mods
gb_settings = {
    "openai_api_key": "",
    "ai_enabled": False,
    "anti_revoke": True,
    "freeze_last_seen": True,
    "anti_blue_tick": True,
    "ghost_mode": True,
    "theme": "dark-oled",  # 'dark-oled', 'midnight-blue', 'neon-purple', 'light'
    "auto_reply_enabled": False,
    "auto_reply_text": "Olá! No momento estou ausente, responderei em breve.",
    "lossless_media": True,
}

# Banco de conversas simuladas
chats_data = {
    1: {
        "name": "Suporte GB Mods 🛡️",
        "avatar": "GB",
        "last_msg": "Bem-vindo ao WhatsApp GB Custom v13!",
        "time": "00:00",
        "messages": [
            {
                "id": 1,
                "sender": "Suporte GB Mods",
                "text": "Bem-vindo ao WhatsApp GB Custom v13! Explore os novos temas e ferramentas no menu 'GB Mods'.",
                "time": "00:00",
                "is_me": False,
                "revoked": False
            }
        ]
    },
    2: {
        "name": "Grupo VIP Desenvolvedores 💻",
        "avatar": "DV",
        "last_msg": "O painel ficou incrível!",
        "time": "Ontem",
        "messages": [
            {
                "id": 1,
                "sender": "Carlos",
                "text": "Galera, testaram o novo tema Roxo Neon?",
                "time": "Ontem",
                "is_me": False,
                "revoked": False
            },
            {
                "id": 2,
                "sender": "Você",
                "text": "O painel ficou incrível!",
                "time": "Ontem",
                "is_me": True,
                "revoked": False
            }
        ]
    },
    3: {
        "name": "Ana Souza 📸",
        "avatar": "AS",
        "last_msg": "Me manda aquela foto em alta resolução?",
        "time": "Seg",
        "messages": [
            {
                "id": 1,
                "sender": "Ana Souza",
                "text": "Me manda aquela foto em alta resolução?",
                "time": "Seg",
                "is_me": False,
                "revoked": False
            }
        ]
    }
}

class MessageModel(BaseModel):
    chat_id: int
    text: str

class RevokeModel(BaseModel):
    chat_id: int
    msg_id: int

class SettingsModel(BaseModel):
    openai_api_key: str
    ai_enabled: bool
    anti_revoke: bool
    freeze_last_seen: bool
    anti_blue_tick: bool
    ghost_mode: bool
    theme: str
    auto_reply_enabled: bool
    auto_reply_text: str
    lossless_media: bool

class ScheduleModel(BaseModel):
    chat_id: int
    text: str
    delay_seconds: int

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp GB Custom v13</title>
    <style>
        :root {
            --bg-color: #0b141a;
            --container-bg: #111b21;
            --header-bg: #202c33;
            --border-color: #2f3b43;
            --text-primary: #e9edef;
            --text-secondary: #8696a0;
            --sent-bg: #005c4b;
            --received-bg: #202c33;
            --accent-color: #00a884;
            --hover-item: #2a3942;
        }

        [data-theme="midnight-blue"] {
            --bg-color: #050b14;
            --container-bg: #0d1b2a;
            --header-bg: #1b263b;
            --border-color: #415a77;
            --sent-bg: #1d3557;
            --received-bg: #1b263b;
            --accent-color: #457b9d;
            --hover-item: #1b263b;
        }

        [data-theme="neon-purple"] {
            --bg-color: #0f051d;
            --container-bg: #1a0b2e;
            --header-bg: #2b124c;
            --border-color: #4d1c8c;
            --sent-bg: #6b21a8;
            --received-bg: #2b124c;
            --accent-color: #a855f7;
            --hover-item: #3b1868;
        }

        [data-theme="light"] {
            --bg-color: #eae6df;
            --container-bg: #ffffff;
            --header-bg: #00a884;
            --border-color: #d1d7db;
            --text-primary: #111b21;
            --text-secondary: #667781;
            --sent-bg: #d9fdd3;
            --received-bg: #ffffff;
            --accent-color: #00a884;
            --hover-item: #f5f6f6;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-primary); display: flex; justify-content: center; align-items: center; height: 100vh; transition: 0.3s; }
        .container { width: 100%; max-width: 480px; height: 100%; background: var(--container-bg); display: flex; flex-direction: column; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.5); overflow: hidden; }
        @media(min-width: 500px) { .container { height: 92vh; border-radius: 12px; } }
        
        /* Header */
        .header { background: var(--header-bg); padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color); min-height: 60px; }
        .header-left { display: flex; align-items: center; gap: 10px; }
        .avatar { width: 40px; height: 40px; background: var(--accent-color); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; flex-shrink: 0; }
        .status-info h3 { font-size: 15px; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px; }
        .status-info p { font-size: 11px; color: var(--text-secondary); }
        .header-btns { display: flex; gap: 4px; }
        .mods-btn, .status-tab-btn, .back-btn { background: var(--accent-color); color: #fff; border: none; padding: 5px 8px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; }
        .mods-btn:hover, .status-tab-btn:hover, .back-btn:hover { opacity: 0.85; }

        /* Views */
        .view-section { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .hidden { display: none !important; }

        /* Home Chat List View */
        .chat-list-body { flex: 1; overflow-y: auto; background: var(--container-bg); }
        .chat-item { display: flex; align-items: center; padding: 12px 16px; gap: 12px; border-bottom: 1px solid var(--border-color); cursor: pointer; transition: 0.2s; }
        .chat-item:hover { background: var(--hover-item); }
        .chat-item-info { flex: 1; min-width: 0; }
        .chat-item-info h4 { font-size: 14px; color: var(--text-primary); margin-bottom: 3px; display: flex; justify-content: space-between; }
        .chat-item-info h4 span { font-size: 11px; color: var(--text-secondary); font-weight: normal; }
        .chat-item-info p { font-size: 12px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        /* Chat Body */
        .chat-body { flex: 1; padding: 16px; overflow-y: auto; background-image: radial-gradient(var(--border-color) 1px, transparent 1px); background-size: 20px 20px; display: flex; flex-direction: column; gap: 8px; }
        .message { max-width: 75%; padding: 8px 12px; border-radius: 8px; position: relative; font-size: 14px; word-break: break-word; color: var(--text-primary); }
        .message.received { background: var(--received-bg); align-self: flex-start; border-top-left-radius: 0; border: 1px solid var(--border-color); }
        .message.sent { background: var(--sent-bg); align-self: flex-end; border-top-right-radius: 0; }
        .message .time { font-size: 10px; color: var(--text-secondary); float: right; margin-left: 8px; margin-top: 4px; line-height: 15px; }
        .revoked-tag { font-style: italic; color: #f15c6d; font-size: 12px; display: block; margin-bottom: 4px; }
        .delete-msg-btn { background: none; border: none; color: var(--text-secondary); font-size: 10px; cursor: pointer; margin-left: 5px; }
        .delete-msg-btn:hover { color: #f15c6d; }
        .badge-lossless { font-size: 9px; background: #00a884; color: #fff; padding: 1px 4px; border-radius: 4px; margin-left: 4px; }

        /* Secondary Bodies (Status / Schedule) */
        .sub-body { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .status-card { background: var(--header-bg); padding: 12px; border-radius: 8px; border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        .status-card img, .status-card video { width: 60px; height: 60px; border-radius: 6px; object-fit: cover; }
        .status-info-box h4 { font-size: 14px; color: var(--text-primary); }
        .status-info-box span { font-size: 11px; color: var(--text-secondary); }
        .download-btn { background: var(--accent-color); color: #fff; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; }

        /* Footer Input */
        .chat-footer { background: var(--header-bg); padding: 10px 16px; display: flex; align-items: center; gap: 8px; border-top: 1px solid var(--border-color); }
        .chat-footer input { flex: 1; background: var(--bg-color); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 8px; color: var(--text-primary); outline: none; font-size: 14px; }
        .chat-footer button { background: var(--accent-color); border: none; color: #fff; padding: 10px 14px; border-radius: 8px; cursor: pointer; font-weight: bold; }

        /* Modal GB Mods */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 100; }
        .modal-content { background: var(--container-bg); padding: 20px; border-radius: 12px; width: 92%; max-width: 420px; border: 1px solid var(--border-color); max-height: 85vh; overflow-y: auto; }
        .modal-content h2 { color: var(--accent-color); margin-bottom: 14px; font-size: 17px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; background: var(--bg-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 6px; color: var(--text-primary); font-size: 13px; }
        .checkbox-group { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 13px; cursor: pointer; color: var(--text-primary); }
        .modal-buttons { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
        .modal-buttons button { padding: 8px 14px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; font-size: 13px; }
        .btn-cancel { background: #334155; color: #cbd5e1; }
        .btn-save { background: var(--accent-color); color: #fff; }
    </style>
</head>
<body data-theme="dark-oled">

    <div class="container">
        <!-- Header Dinâmico -->
        <div class="header">
            <div class="header-left" id="header-left-content">
                <div class="avatar">GB</div>
                <div class="status-info">
                    <h3>WhatsApp GB Custom</h3>
                    <p>Online (Modo Fantasma)</p>
                </div>
            </div>
            <div class="header-btns" id="header-buttons">
                <button class="status-tab-btn" onclick="toggleView('status')">Status 📸</button>
                <button class="status-tab-btn" onclick="toggleView('schedule')">Agendar ⏰</button>
                <button class="mods-btn" onclick="openMods()">⚙️ Mods</button>
            </div>
        </div>

        <!-- View 1: Lista de Conversas (Home) -->
        <div id="home-view" class="view-section">
            <div class="chat-list-body" id="chat-list">
                <!-- Preenchido via JavaScript -->
            </div>
        </div>

        <!-- View 2: Tela de Chat Individual -->
        <div id="chat-view" class="view-section hidden">
            <div class="chat-body" id="chat-body"></div>
            <div class="chat-footer">
                <input type="text" id="message-input" placeholder="Digite uma mensagem..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Enviar</button>
            </div>
        </div>

        <!-- View 3: Status Viewer -->
        <div id="status-view" class="view-section hidden">
            <div class="sub-body">
                <h3 style="font-size: 15px; color: var(--accent-color); margin-bottom: 4px;">Status de Contatos (GB Downloader)</h3>
                <div class="status-card">
                    <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500" alt="Status">
                    <div class="status-info-box">
                        <h4>Ana Souza</h4>
                        <span>Postado há 2 horas (Foto HD)</span>
                    </div>
                    <button class="download-btn" onclick="alert('Status baixado em alta resolução com sucesso!')">Baixar</button>
                </div>
                <div class="status-card">
                    <video src="https://assets.mixkit.co/videos/preview/mixkit-tree-branches-in-the-breeze-1186-large.mp4" muted autoplay loop></video>
                    <div class="status-info-box">
                        <h4>Carlos Tech</h4>
                        <span>Postado há 5 horas (Vídeo)</span>
                    </div>
                    <button class="download-btn" onclick="alert('Vídeo de status baixado com sucesso!')">Baixar</button>
                </div>
            </div>
        </div>

        <!-- View 4: Agendador de Mensagens -->
        <div id="schedule-view" class="view-section hidden">
            <div class="sub-body">
                <h3 style="font-size: 15px; color: var(--accent-color);">⏰ Agendador de Disparos</h3>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Selecione a Conversa Destino</label>
                    <select id="sched-chat-select">
                        <option value="1">Suporte GB Mods</option>
                        <option value="2">Grupo VIP Desenvolvedores</option>
                        <option value="3">Ana Souza</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Mensagem a ser enviada</label>
                    <input type="text" id="sched-text" placeholder="Ex: Bom dia automático!">
                </div>
                <div class="form-group">
                    <label>Disparar em quantos segundos?</label>
                    <input type="number" id="sched-delay" value="10">
                </div>
                <button class="download-btn" onclick="scheduleMessage()">Agendar Disparo</button>
                <div id="sched-list" style="margin-top: 15px; font-size: 13px; color: var(--text-secondary);"></div>
            </div>
        </div>
    </div>

    <!-- Modal GB Mods -->
    <div class="modal" id="mods-modal">
        <div class="modal-content">
            <h2>⚙️ Painel GB Mods v13</h2>
            
            <div class="form-group">
                <label>Tema Visual e Cores</label>
                <select id="theme-select">
                    <option value="dark-oled">Preto OLED (Padrão Dark)</option>
                    <option value="midnight-blue">Azul Meia-Noite</option>
                    <option value="neon-purple">Roxo Neon</option>
                    <option value="light">Modo Claro Clássico</option>
                </select>
            </div>

            <div class="form-group">
                <label>Chave da API OpenAI (ChatGPT)</label>
                <input type="password" id="api-key" placeholder="sk-...">
            </div>

            <div class="form-group">
                <label>Status da Inteligência Artificial</label>
                <select id="ai-status">
                    <option value="false">Desativado (Modo Manual Puro)</option>
                    <option value="true">Ativado (ChatGPT)</option>
                </select>
            </div>

            <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 12px 0;">

            <div class="form-group">
                <label>Mensagem Automática de Ausência (Auto-Reply)</label>
                <input type="text" id="auto-reply-text">
            </div>

            <label class="checkbox-group">
                <input type="checkbox" id="auto-reply-enabled"> 🤖 Ativar Resposta Automática
            </label>
            <label class="checkbox-group">
                <input type="checkbox" id="lossless-media"> 📷 Enviar Mídia em Qualidade Máxima (Lossless)
            </label>
            <label class="checkbox-group">
                <input type="checkbox" id="anti-revoke"> 🛡️ Anti-Revogação (Impedir apagar mensagens)
            </label>
            <label class="checkbox-group">
                <input type="checkbox" id="freeze-last-seen"> ❄️ Congelar Visto por Último
            </label>
            <label class="checkbox-group">
                <input type="checkbox" id="anti-blue-tick"> 👀 Ocultar Confirmação de Leitura
            </label>
            <label class="checkbox-group">
                <input type="checkbox" id="ghost-mode"> 👻 Ocultar "Digitando..."
            </label>

            <div class="modal-buttons">
                <button class="btn-cancel" onclick="closeMods()">Cancelar</button>
                <button class="btn-save" onclick="saveMods()">Salvar Alterações</button>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;

        function toggleView(view) {
            document.getElementById('home-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('status-view').classList.add('hidden');
            document.getElementById('schedule-view').classList.add('hidden');

            const headerLeft = document.getElementById('header-left-content');
            const headerBtns = document.getElementById('header-buttons');

            if (view === 'home') {
                document.getElementById('home-view').classList.remove('hidden');
                headerLeft.innerHTML = `
                    <div class="avatar">GB</div>
                    <div class="status-info">
                        <h3>WhatsApp GB Custom</h3>
                        <p>Online (Modo Fantasma)</p>
                    </div>`;
                headerBtns.innerHTML = `
                    <button class="status-tab-btn" onclick="toggleView('status')">Status 📸</button>
                    <button class="status-tab-btn" onclick="toggleView('schedule')">Agendar ⏰</button>
                    <button class="mods-btn" onclick="openMods()">⚙️ Mods</button>`;
                loadChatList();
            } else if (view === 'chat') {
                document.getElementById('chat-view').classList.remove('hidden');
                headerBtns.innerHTML = `<button class="back-btn" onclick="toggleView('home')">⬅️ Voltar</button>`;
                loadCurrentChat();
            } else if (view === 'status' || view === 'schedule') {
                if (view === 'status') document.getElementById('status-view').classList.remove('hidden');
                if (view === 'schedule') document.getElementById('schedule-view').classList.remove('hidden');
                
                headerLeft.innerHTML = `
                    <div class="status-info">
                        <h3 style="font-size:16px;">${view === 'status' ? 'Status 📸' : 'Agendador ⏰'}</h3>
                    </div>`;
                headerBtns.innerHTML = `<button class="back-btn" onclick="toggleView('home')">⬅️ Voltar ao Início</button>`;
            }
        }

        function loadAppData() {
            fetch('/get_data')
                .then(res => res.json())
                .then(data => {
                    document.body.setAttribute('data-theme', data.theme);
                    if (document.getElementById('home-view').classList.contains('hidden') === false) {
                        renderChatList(data.chats);
                    } else if (currentChatId !== null) {
                        renderMessages(data.chats[currentChatId]);
                    }
                });
        }

        function loadChatList() {
            fetch('/get_data')
                .then(res => res.json())
                .then(data => {
                    document.body.setAttribute('data-theme', data.theme);
                    renderChatList(data.chats);
                });
        }

        function renderChatList(chats) {
            const listContainer = document.getElementById('chat-list');
            listContainer.innerHTML = '';
            for (const [id, chat] of Object.entries(chats)) {
                let div = document.createElement('div');
                div.className = 'chat-item';
                div.onclick = () => openChat(id, chat.name);
                div.innerHTML = `
                    <div class="avatar">${chat.avatar}</div>
                    <div class="chat-item-info">
                        <h4>${chat.name} <span>${chat.time}</span></h4>
                        <p>${chat.last_msg}</p>
                    </div>
                `;
                listContainer.appendChild(div);
            }
        }

        function openChat(id, name) {
            currentChatId = id;
            document.getElementById('header-left-content').innerHTML = `
                <div class="avatar">${name.substring(0,2).toUpperCase()}</div>
                <div class="status-info">
                    <h3>${name}</h3>
                    <p>Online</p>
                </div>`;
            toggleView('chat');
        }

        function loadCurrentChat() {
            if (!currentChatId) return;
            fetch('/get_data')
                .then(res => res.json())
                .then(data => {
                    renderMessages(data.chats[currentChatId]);
                });
        }

        function renderMessages(chat) {
            const chatBody = document.getElementById('chat-body');
            chatBody.innerHTML = '';
            chat.messages.forEach(msg => {
                let div = document.createElement('div');
                div.className = `message ${msg.is_me ? 'sent' : 'received'}`;
                
                let content = '';
                if (msg.revoked) {
                    content += `<span class="revoked-tag">🚫 [Esta mensagem foi apagada pelo contato]</span>`;
                }
                content += `<span>${msg.text}</span>`;
                content += `<span class="time">${msg.time}</span>`;
                
                if (!msg.is_me) {
                    content += `<button class="delete-msg-btn" onclick="revokeMessage(${currentChatId}, ${msg.id})" title="Apagar">[Apagar]</button>`;
                }

                div.innerHTML = content;
                chatBody.appendChild(div);
            });
            chatBody.scrollTop = chatBody.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('message-input');
            const text = input.value.trim();
            if (!text || !currentChatId) return;

            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chat_id: parseInt(currentChatId), text: text })
            }).then(() => {
                input.value = '';
                loadCurrentChat();
            });
        }

        function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }

        function revokeMessage(chatId, msgId) {
            fetch('/revoke_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chat_id: chatId, msg_id: msgId })
            }).then(() => loadCurrentChat());
        }

        function scheduleMessage() {
            const chatId = document.getElementById('sched-chat-select').value;
            const text = document.getElementById('sched-text').value;
            const delay = document.getElementById('sched-delay').value;
            if(!text) return alert('Digite a mensagem!');

            fetch('/schedule_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chat_id: parseInt(chatId), text: text, delay_seconds: parseInt(delay) })
            }).then(res => res.json()).then(data => {
                alert(data.status);
                document.getElementById('sched-list').innerHTML = `Última agendada: "${text}" para daqui a ${delay}s.`;
            });
        }

        function openMods() {
            fetch('/get_settings')
                .then(res => res.json())
                .then(settings => {
                    document.getElementById('theme-select').value = settings.theme;
                    document.getElementById('api-key').value = settings.openai_api_key;
                    document.getElementById('ai-status').value = settings.ai_enabled.toString();
                    document.getElementById('auto-reply-enabled').checked = settings.auto_reply_enabled;
                    document.getElementById('auto-reply-text').value = settings.auto_reply_text;
                    document.getElementById('lossless-media').checked = settings.lossless_media;
                    document.getElementById('anti-revoke').checked = settings.anti_revoke;
                    document.getElementById('freeze-last-seen').checked = settings.freeze_last_seen;
                    document.getElementById('anti-blue-tick').checked = settings.anti_blue_tick;
                    document.getElementById('ghost-mode').checked = settings.ghost_mode;
                    document.getElementById('mods-modal').style.display = 'flex';
                });
        }

        function closeMods() { document.getElementById('mods-modal').style.display = 'none'; }

        function saveMods() {
            const settings = {
                theme: document.getElementById('theme-select').value,
                openai_api_key: document.getElementById('api-key').value,
                ai_enabled: document.getElementById('ai-status').value === 'true',
                auto_reply_enabled: document.getElementById('auto-reply-enabled').checked,
                auto_reply_text: document.getElementById('auto-reply-text').value,
                lossless_media: document.getElementById('lossless-media').checked,
                anti_revoke: document.getElementById('anti-revoke').checked,
                freeze_last_seen: document.getElementById('freeze-last-seen').checked,
                anti-blue-tick: document.getElementById('anti-blue-tick').checked,
                ghost_mode: document.getElementById('ghost-mode').checked
            };
            // Correção da chave anti-blue-tick no objeto abaixo
            settings.anti_blue_tick = document.getElementById('anti-blue-tick').checked;

            fetch('/save_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            }).then(() => {
                closeMods();
                loadChatList();
                alert('Configurações GB v13 salvas com sucesso!');
            });
        }

        setInterval(loadAppData, 3000);
        loadChatList();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TEMPLATE

@app.get("/get_data")
def get_data():
    return {
        "chats": chats_data,
        "theme": gb_settings["theme"]
    }

@app.post("/send_message")
def send_message(data: MessageModel):
    now = datetime.now().strftime("%H:%M")
    chat = chats_data.get(data.chat_id)
    if not chat:
        return {"status": "error"}

    # Adiciona a mensagem do usuário
    msg_id = len(chat["messages"]) + 1
    chat["messages"].append({"id": msg_id, "sender": "Você", "text": data.text, "time": now, "is_me": True, "revoked": False})
    chat["last_msg"] = f"Você: {data.text}"
    chat["time"] = now

    # Resposta Inteligente (IA) ou Auto-Reply
    if gb_settings["ai_enabled"] and gb_settings["openai_api_key"]:
        resp_text = f"🤖 [ChatGPT] Resposta para: '{data.text}'"
    elif gb_settings["auto_reply_enabled"]:
        resp_text = f"⚡ [Auto-Reply GB] {gb_settings['auto_reply_text']}"
    else:
        return {"status": "success"}

    resp_id = len(chat["messages"]) + 1
    chat["messages"].append({"id": resp_id, "sender": chat["name"], "text": resp_text, "time": datetime.now().strftime("%H:%M"), "is_me": False, "revoked": False})
    chat["last_msg"] = resp_text
    chat["time"] = datetime.now().strftime("%H:%M")
    return {"status": "success"}

@app.post("/revoke_message")
def revoke_message(data: RevokeModel):
    chat = chats_data.get(data.chat_id)
    if not chat:
        return {"status": "error"}
    for m in chat["messages"]:
        if m["id"] == data.msg_id:
            if gb_settings["anti_revoke"]:
                m["revoked"] = True
            else:
                m["text"] = "Esta mensagem foi apagada."
    return {"status": "success"}

@app.post("/schedule_message")
async def schedule_message(data: ScheduleModel):
    async def delayed_task():
        await asyncio.sleep(data.delay_seconds)
        now = datetime.now().strftime("%H:%M")
        chat = chats_data.get(data.chat_id)
        if chat:
            msg_id = len(chat["messages"]) + 1
            chat["messages"].append({"id": msg_id, "sender": "Você (Agendado)", "text": data.text, "time": now, "is_me": True, "revoked": False})
            chat["last_msg"] = f"Agendado: {data.text}"
            chat["time"] = now
    
    asyncio.create_task(delayed_task())
    return {"status": f"Mensagem agendada com sucesso para daqui a {data.delay_seconds} segundos!"}

@app.get("/get_settings")
def get_settings():
    return gb_settings

@app.post("/save_settings")
def save_settings(data: SettingsModel):
    gb_settings.update(data.dict())
    return {"status": "success"}
