from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import asyncio
import requests

app = FastAPI()

# Configurações da Evolution API
EVOLUTION_URL = "https://evolution.mxbr.com.br"
INSTANCE_NAME = "EnjoyWeb"
EVOLUTION_API_KEY = "429683C4C977415CAAFCCE10F7D57E11"

headers = {
    "apikey": EVOLUTION_API_KEY,
    "Content-Type": "application/json"
}

# Configurações do GB Mods
gb_settings = {
    "openai_api_key": "",
    "ai_enabled": False,
    "anti_revoke": True,
    "freeze_last_seen": True,
    "anti_blue_tick": True,
    "ghost_mode": True,
    "theme": "dark-oled",
    "auto_reply_enabled": False,
    "auto_reply_text": "Olá! No momento estou ausente, responderei em breve.",
    "lossless_media": True,
}

class MessageModel(BaseModel):
    chat_id: str
    text: str

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
    chat_id: str
    text: str
    delay_seconds: int

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp GB Custom v13 - Evolution API</title>
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
            --bg-color: #050b14; --container-bg: #0d1b2a; --header-bg: #1b263b; --border-color: #415a77; --sent-bg: #1d3557; --received-bg: #1b263b; --accent-color: #457b9d; --hover-item: #1b263b;
        }
        [data-theme="neon-purple"] {
            --bg-color: #0f051d; --container-bg: #1a0b2e; --header-bg: #2b124c; --border-color: #4d1c8c; --sent-bg: #6b21a8; --received-bg: #2b124c; --accent-color: #a855f7; --hover-item: #3b1868;
        }
        [data-theme="light"] {
            --bg-color: #eae6df; --container-bg: #ffffff; --header-bg: #00a884; --border-color: #d1d7db; --text-primary: #111b21; --text-secondary: #667781; --sent-bg: #d9fdd3; --received-bg: #ffffff; --accent-color: #00a884; --hover-item: #f5f6f6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-primary); display: flex; justify-content: center; align-items: center; height: 100vh; transition: 0.3s; }
        .container { width: 100%; max-width: 480px; height: 100%; background: var(--container-bg); display: flex; flex-direction: column; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.5); overflow: hidden; }
        @media(min-width: 500px) { .container { height: 92vh; border-radius: 12px; } }
        .header { background: var(--header-bg); padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color); min-height: 65px; z-index: 5; }
        .header-left { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
        .avatar { width: 40px; height: 40px; background: var(--accent-color); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; flex-shrink: 0; overflow: hidden; }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
        .status-info h3 { font-size: 15px; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .status-info p { font-size: 11px; color: var(--text-secondary); }
        .header-btns { display: flex; gap: 4px; flex-shrink: 0; }
        .mods-btn, .status-tab-btn, .back-btn { background: var(--accent-color); color: #fff; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; }
        
        .view-section { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .hidden { display: none !important; }
        .chat-list-body { flex: 1; overflow-y: auto; background: var(--container-bg); position: relative; padding-bottom: 70px; }
        .chat-item { display: flex; align-items: center; padding: 12px 16px; gap: 12px; border-bottom: 1px solid var(--border-color); cursor: pointer; transition: 0.2s; }
        .chat-item:hover { background: var(--hover-item); }
        .chat-item-info { flex: 1; min-width: 0; }
        .chat-item-info h4 { font-size: 14px; color: var(--text-primary); margin-bottom: 3px; display: flex; justify-content: space-between; }
        .chat-item-info h4 span { font-size: 11px; color: var(--text-secondary); font-weight: normal; }
        .chat-item-info p { font-size: 12px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        .fab-btn { position: absolute; bottom: 20px; right: 20px; background: var(--accent-color); color: #fff; width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.6); border: none; z-index: 50; transition: transform 0.2s; }
        .fab-btn:hover { transform: scale(1.08); }

        .chat-body { flex: 1; padding: 16px; overflow-y: auto; background-image: radial-gradient(var(--border-color) 1px, transparent 1px); background-size: 20px 20px; display: flex; flex-direction: column; gap: 8px; }
        .message { max-width: 75%; padding: 8px 12px; border-radius: 8px; position: relative; font-size: 14px; word-break: break-word; color: var(--text-primary); }
        .message.received { background: var(--received-bg); align-self: flex-start; border-top-left-radius: 0; border: 1px solid var(--border-color); }
        .message.sent { background: var(--sent-bg); align-self: flex-end; border-top-right-radius: 0; }
        .message .time { font-size: 10px; color: var(--text-secondary); float: right; margin-left: 8px; margin-top: 4px; line-height: 15px; }
        .sub-body { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .status-card { background: var(--header-bg); padding: 12px; border-radius: 8px; border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        .status-card img { width: 60px; height: 60px; border-radius: 6px; object-fit: cover; }
        .status-info-box h4 { font-size: 14px; color: var(--text-primary); }
        .status-info-box span { font-size: 11px; color: var(--text-secondary); }
        .download-btn { background: var(--accent-color); color: #fff; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; }
        .chat-footer { background: var(--header-bg); padding: 10px 16px; display: flex; align-items: center; gap: 8px; border-top: 1px solid var(--border-color); }
        .chat-footer input { flex: 1; background: var(--bg-color); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 8px; color: var(--text-primary); outline: none; font-size: 14px; }
        .chat-footer button { background: var(--accent-color); border: none; color: #fff; padding: 10px 14px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 100; }
        .modal-content { background: var(--container-bg); padding: 20px; border-radius: 12px; width: 92%; max-width: 420px; border: 1px solid var(--border-color); max-height: 85vh; overflow-y: auto; }
        .modal-content h2 { color: var(--accent-color); margin-bottom: 14px; font-size: 17px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
        .form-group input, .form-group select { width: 100%; background: var(--bg-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 6px; color: var(--text-primary); font-size: 13px; }
        .checkbox-group { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 13px; cursor: pointer; color: var(--text-primary); }
        .modal-buttons { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
        .modal-buttons button { padding: 8px 14px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; font-size: 13px; }
        .btn-cancel { background: #334155; color: #cbd5e1; }
        .btn-save { background: var(--accent-color); color: #fff; }
    </style>
</head>
<body data-theme="dark-oled">
    <div class="container">
        <div class="header">
            <div class="header-left" id="header-left-content">
                <div class="avatar" id="my-avatar">WA</div>
                <div class="status-info">
                    <h3 id="my-name">Carregando...</h3>
                    <p>Online (Evolution API)</p>
                </div>
            </div>
            <div class="header-btns" id="header-buttons">
                <button class="status-tab-btn" onclick="navigateTo('status')">Status 📸</button>
                <button class="status-tab-btn" onclick="navigateTo('schedule')">Agendar ⏰</button>
                <button class="mods-btn" onclick="openMods()">⚙️ Mods</button>
            </div>
        </div>

        <div id="home-view" class="view-section">
            <div class="chat-list-body" id="chat-list"></div>
            <button class="fab-btn" onclick="openContactsModal()" title="Nova Conversa">💬</button>
        </div>

        <div id="chat-view" class="view-section hidden">
            <div class="chat-body" id="chat-body"></div>
            <div class="chat-footer">
                <input type="text" id="message-input" placeholder="Digite uma mensagem..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Enviar</button>
            </div>
        </div>

        <div id="status-view" class="view-section hidden">
            <div class="sub-body">
                <h3 style="font-size: 15px; color: var(--accent-color); margin-bottom: 4px;">Status de Contatos (GB Downloader)</h3>
                <div class="status-card">
                    <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500" alt="Status">
                    <div class="status-info-box">
                        <h4>Contato Status</h4>
                        <span>Postado recentemente</span>
                    </div>
                    <button class="download-btn" onclick="alert('Status baixado com sucesso!')">Baixar</button>
                </div>
            </div>
        </div>

        <div id="schedule-view" class="view-section hidden">
            <div class="sub-body">
                <h3 style="font-size: 15px; color: var(--accent-color);">⏰ Agendador de Disparos</h3>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Número do WhatsApp Destino (com DDI e DDD)</label>
                    <input type="text" id="sched-number" placeholder="Ex: 5543999999999">
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

    <!-- Modal de Contatos com Busca -->
    <div class="modal" id="contacts-modal">
        <div class="modal-content">
            <h2>👥 Iniciar Conversa com Contato</h2>
            <div class="form-group">
                <label>Pesquisar nome ou número</label>
                <input type="text" id="contact-search-input" placeholder="Digite para buscar..." oninput="filterContacts()">
            </div>
            <div id="contacts-modal-list" style="max-height: 300px; overflow-y: auto; margin-top: 10px;">
                <p style="text-align: center; color: var(--text-secondary);">Carregando contatos...</p>
            </div>
            <div class="modal-buttons" style="margin-top: 14px;">
                <button class="btn-cancel" onclick="closeContactsModal()">Fechar</button>
            </div>
        </div>
    </div>

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
            <label class="checkbox-group"><input type="checkbox" id="auto-reply-enabled"> 🤖 Ativar Resposta Automática</label>
            <label class="checkbox-group"><input type="checkbox" id="lossless-media"> 📷 Enviar Mídia em Qualidade Máxima</label>
            <label class="checkbox-group"><input type="checkbox" id="anti-revoke"> 🛡️ Anti-Revogação (Impedir apagar mensagens)</label>
            <label class="checkbox-group"><input type="checkbox" id="freeze-last-seen"> ❄️ Congelar Visto por Último</label>
            <label class="checkbox-group"><input type="checkbox" id="anti-blue-tick"> 👀 Ocultar Confirmação de Leitura</label>
            <label class="checkbox-group"><input type="checkbox" id="ghost-mode"> 👻 Ocultar "Digitando..."</label>
            <div class="modal-buttons">
                <button class="btn-cancel" onclick="closeMods()">Cancelar</button>
                <button class="btn-save" onclick="saveMods()">Salvar Alterações</button>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        let currentChatName = '';
        let currentView = 'home';
        let allContactsCache = [];

        function navigateTo(view) {
            currentView = view;
            document.getElementById('home-view').classList.add('hidden');
            document.getElementById('chat-view').classList.add('hidden');
            document.getElementById('status-view').classList.add('hidden');
            document.getElementById('schedule-view').classList.add('hidden');

            const headerBtns = document.getElementById('header-buttons');

            if (view === 'home') {
                document.getElementById('home-view').classList.remove('hidden');
                loadProfileHeader();
                headerBtns.innerHTML = `
                    <button class="status-tab-btn" onclick="navigateTo('status')">Status 📸</button>
                    <button class="status-tab-btn" onclick="navigateTo('schedule')">Agendar ⏰</button>
                    <button class="mods-btn" onclick="openMods()">⚙️ Mods</button>`;
                refreshData();
            } else if (view === 'chat') {
                document.getElementById('chat-view').classList.remove('hidden');
                headerBtns.innerHTML = `<button class="back-btn" onclick="navigateTo('home')">⬅️ Voltar</button>`;
            } else if (view === 'status' || view === 'schedule') {
                if (view === 'status') document.getElementById('status-view').classList.remove('hidden');
                if (view === 'schedule') document.getElementById('schedule-view').classList.remove('hidden');
                
                const headerLeft = document.getElementById('header-left-content');
                headerLeft.innerHTML = `<div class="status-info"><h3 style="font-size:16px;">${view === 'status' ? 'Status 📸' : 'Agendador ⏰'}</h3></div>`;
                headerBtns.innerHTML = `<button class="back-btn" onclick="navigateTo('home')">⬅️ Voltar</button>`;
            }
        }

        function loadProfileHeader() {
            fetch('/get_profile')
                .then(res => res.json())
                .then(data => {
                    const headerLeft = document.getElementById('header-left-content');
                    let avatarHTML = data.pic ? `<img src="${data.pic}" alt="Perfil">` : (data.name || "WA").substring(0,2).toUpperCase();
                    
                    headerLeft.innerHTML = `
                        <div class="avatar" id="my-avatar">${avatarHTML}</div>
                        <div class="status-info">
                            <h3 id="my-name">${data.name || "WhatsApp EnjoyWeb"}</h3>
                            <p>Online (Evolution API)</p>
                        </div>
                    `;
                });
        }

        function refreshData() {
            fetch('/get_chats')
                .then(res => res.json())
                .then(data => {
                    document.body.setAttribute('data-theme', data.theme);
                    if (currentView === 'home') {
                        renderChatList(data.chats);
                    }
                });
        }

        function renderChatList(chats) {
            const listContainer = document.getElementById('chat-list');
            listContainer.innerHTML = '';
            if (chats.length === 0) {
                listContainer.innerHTML = '<div style="padding: 40px 20px; text-align: center; color: var(--text-secondary);"><p style="font-size:15px; margin-bottom:6px;">Nenhum chat recente.</p><p style="font-size:12px;">Clique no botão flutuante 💬 abaixo para buscar um contato e iniciar uma conversa.</p></div>';
                return;
            }
            chats.forEach(chat => {
                let div = document.createElement('div');
                div.className = 'chat-item';
                div.onclick = () => openChat(chat.id, chat.name, chat.pic);
                let avatarHTML = chat.pic ? `<img src="${chat.pic}" alt="Avatar">` : chat.name.substring(0,2).toUpperCase();
                div.innerHTML = `
                    <div class="avatar">${avatarHTML}</div>
                    <div class="chat-item-info">
                        <h4>${chat.name} <span>${chat.time || ''}</span></h4>
                        <p>${chat.last_msg || chat.id}</p>
                    </div>
                `;
                listContainer.appendChild(div);
            });
        }

        function openContactsModal() {
            document.getElementById('contacts-modal').style.display = 'flex';
            document.getElementById('contact-search-input').value = '';
            fetch('/get_contacts')
                .then(res => res.json())
                .then(data => {
                    allContactsCache = data.contacts || [];
                    renderContactModalList(allContactsCache);
                });
        }

        function closeContactsModal() {
            document.getElementById('contacts-modal').style.display = 'none';
        }

        function filterContacts() {
            const query = document.getElementById('contact-search-input').value.toLowerCase();
            const filtered = allContactsCache.filter(c => 
                c.name.toLowerCase().includes(query) || c.id.toLowerCase().includes(query)
            );
            renderContactModalList(filtered);
        }

        function renderContactModalList(contacts) {
            const container = document.getElementById('contacts-modal-list');
            container.innerHTML = '';
            if (contacts.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 10px;">Nenhum contato encontrado.</p>';
                return;
            }
            contacts.forEach(c => {
                let div = document.createElement('div');
                div.className = 'chat-item';
                div.onclick = () => {
                    closeContactsModal();
                    openChat(c.id, c.name, c.pic);
                };
                let avatarHTML = c.pic ? `<img src="${c.pic}" alt="Avatar">` : c.name.substring(0,2).toUpperCase();
                div.innerHTML = `
                    <div class="avatar">${avatarHTML}</div>
                    <div class="chat-item-info">
                        <h4>${c.name}</h4>
                        <p>${c.id}</p>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        function openChat(id, name, pic) {
            currentChatId = id;
            currentChatName = name;
            let avatarHTML = pic ? `<img src="${pic}" alt="Avatar">` : name.substring(0,2).toUpperCase();
            
            document.getElementById('header-left-content').innerHTML = `
                <div class="avatar">${avatarHTML}</div>
                <div class="status-info">
                    <h3>${name}</h3>
                    <p>${id}</p>
                </div>`;
            navigateTo('chat');
            loadMessages(id);
        }

        function loadMessages(chatId) {
            fetch(`/get_messages?chat_id=${encodeURIComponent(chatId)}`)
                .then(res => res.json())
                .then(data => {
                    const chatBody = document.getElementById('chat-body');
                    chatBody.innerHTML = '';
                    if(data.messages.length === 0) {
                        chatBody.innerHTML = '<div style="text-align:center; color:var(--text-secondary); margin-top:20px;">Nenhuma mensagem neste chat ainda. Envie uma mensagem abaixo!</div>';
                        return;
                    }
                    data.messages.forEach(msg => {
                        let div = document.createElement('div');
                        div.className = `message ${msg.is_me ? 'sent' : 'received'}`;
                        div.innerHTML = `<span>${msg.text}</span><span class="time">${msg.time}</span>`;
                        chatBody.appendChild(div);
                    });
                    chatBody.scrollTop = chatBody.scrollHeight;
                });
        }

        function sendMessage() {
            const input = document.getElementById('message-input');
            const text = input.value.trim();
            if (!text || !currentChatId) return;

            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chat_id: currentChatId, text: text })
            }).then(res => res.json()).then(data => {
                input.value = '';
                loadMessages(currentChatId);
            });
        }

        function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }

        function scheduleMessage() {
            const number = document.getElementById('sched-number').value.trim();
            const text = document.getElementById('sched-text').value;
            const delay = document.getElementById('sched-delay').value;
            if(!number || !text) return alert('Preencha o número e a mensagem!');

            fetch('/schedule_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chat_id: number, text: text, delay_seconds: parseInt(delay) })
            }).then(res => res.json()).then(data => {
                alert(data.status);
                document.getElementById('sched-list').innerHTML = `Agendado para ${number} daqui a ${delay}s.`;
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
                anti_blue_tick: document.getElementById('anti-blue-tick').checked,
                ghost_mode: document.getElementById('ghost-mode').checked
            };
            fetch('/save_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            }).then(() => {
                closeMods();
                refreshData();
                alert('Configurações salvas!');
            });
        }

        setInterval(() => {
            if (currentView === 'home') {
                refreshData();
            } else if (currentView === 'chat' && currentChatId) {
                loadMessages(currentChatId);
            }
        }, 5000);

        navigateTo('home');
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TEMPLATE

@app.get("/get_profile")
def get_profile():
    profile_name = INSTANCE_NAME
    profile_pic = ""
    try:
        url = f"{EVOLUTION_URL}/instance/fetchInstances"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            instances = data if isinstance(data, list) else data.get("instances", [])
            for inst in instances:
                if inst.get("name") == INSTANCE_NAME or inst.get("instance", {}).get("instanceName") == INSTANCE_NAME:
                    profile = inst.get("profileName") or inst.get("ownerJid", "").split("@")[0]
                    if profile:
                        profile_name = profile
                    profile_pic = inst.get("profilePictureUrl") or inst.get("profilePicUrl", "")
                    break
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
    
    return {"name": profile_name, "pic": profile_pic}

@app.get("/get_chats")
def get_chats():
    chats_list = []
    try:
        url = f"{EVOLUTION_URL}/chat/findChats/{INSTANCE_NAME}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            items = data if isinstance(data, list) else data.get("chats", [])
            for c in items:
                jid = c.get("id") or c.get("remoteJid", "")
                name = c.get("name") or c.get("pushName") or jid.split("@")[0]
                pic = c.get("profilePictureUrl") or c.get("pictureUrl", "")
                last_message = c.get("lastMessage", {})
                last_text = last_message.get("conversation") or last_message.get("text") or "Conversa ativa"
                
                chats_list.append({
                    "id": jid,
                    "name": name,
                    "last_msg": last_text,
                    "pic": pic,
                    "time": ""
                })
    except Exception as e:
        print(f"Erro ao buscar chats: {e}")

    return {
        "chats": chats_list,
        "theme": gb_settings["theme"]
    }

@app.get("/get_contacts")
def get_contacts():
    contacts_list = []
    try:
        url_contacts = f"{EVOLUTION_URL}/chat/findContacts/{INSTANCE_NAME}"
        res_c = requests.post(url_contacts, json={}, headers=headers, timeout=5)
        if res_c.status_code == 200:
            c_data = res_c.json()
            c_items = c_data if isinstance(c_data, list) else c_data.get("contacts", [])
            for c in c_items:
                jid = c.get("id") or c.get("remoteJid", "")
                name = c.get("name") or c.get("pushName") or jid.split("@")[0]
                pic = c.get("profilePictureUrl", "")
                contacts_list.append({
                    "id": jid,
                    "name": name,
                    "pic": pic
                })
    except Exception as e:
        print(f"Erro ao buscar contatos: {e}")

    if not contacts_list:
        contacts_list.append({
            "id": "5543999999999@s.whatsapp.net",
            "name": "Exemplo Contato",
            "pic": ""
        })

    return {"contacts": contacts_list}

@app.get("/get_messages")
def get_messages(chat_id: str):
    msgs = []
    try:
        url = f"{EVOLUTION_URL}/chat/findMessages/{INSTANCE_NAME}"
        payload = {"where": {"remoteJid": chat_id}}
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            messages_data = []
            if isinstance(data, list):
                messages_data = data
            elif isinstance(data, dict):
                messages_data = data.get("messages", {}).get("records", []) or data.get("messages", []) or data.get("records", [])
            
            for m in messages_data:
                msg_obj = m.get("message", {})
                body = (
                    msg_obj.get("conversation") or 
                    msg_obj.get("extendedTextMessage", {}).get("text") or 
                    msg_obj.get("imageMessage", {}).get("caption") or 
                    "[Mídia/Mensagem]"
                )
                from_me = m.get("key", {}).get("fromMe", False)
                timestamp = m.get("messageTimestamp", 0)
                try:
                    time_str = datetime.fromtimestamp(int(timestamp)).strftime("%H:%M") if timestamp else ""
                except:
                    time_str = ""
                
                msgs.append({
                    "text": str(body),
                    "is_me": from_me,
                    "time": time_str
                })
    except Exception as e:
        print(f"Erro ao buscar mensagens: {e}")

    return {"messages": msgs}

@app.post("/send_message")
def send_message(data: MessageModel):
    try:
        url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
        payload = {
            "number": data.chat_id,
            "text": data.text,
            "delay": 1200
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return {"status": "success", "response": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/schedule_message")
async def schedule_message(data: ScheduleModel):
    async def delayed_task():
        await asyncio.sleep(data.delay_seconds)
        try:
            url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
            payload = {
                "number": data.chat_id,
                "text": data.text,
                "delay": 1200
            }
            requests.post(url, json=payload, headers=headers, timeout=10)
        except Exception as e:
            print(f"Erro no agendamento: {e}")
    
    asyncio.create_task(delayed_task())
    return {"status": f"Mensagem agendada com sucesso para daqui a {data.delay_seconds} segundos!"}

@app.get("/get_settings")
def get_settings():
    return gb_settings

@app.post("/save_settings")
def save_settings(data: SettingsModel):
    gb_settings.update(data.dict())
    return {"status": "success"}
