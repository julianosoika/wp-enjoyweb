from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import asyncio
import requests

app = FastAPI()

EVOLUTION_URL = "https://evolution.mxbr.com.br"
INSTANCE_NAME = "EnjoyWeb"
EVOLUTION_API_KEY = "429683C4C977415CAAFCCE10F7D57E11"

headers = {
    "apikey": EVOLUTION_API_KEY,
    "Content-Type": "application/json"
}

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

class MassModel(BaseModel):
    numbers: list
    text: str

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp GB Custom v17 - Evolution API</title>
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
        [data-theme="light"] {
            --bg-color: #eae6df; --container-bg: #ffffff; --header-bg: #00a884; --border-color: #d1d7db; --text-primary: #111b21; --text-secondary: #667781; --sent-bg: #d9fdd3; --received-bg: #ffffff; --accent-color: #00a884; --hover-item: #f5f6f6;
        }
        [data-theme="lime-black"] {
            --bg-color: #0a0a0a; --container-bg: #121212; --header-bg: #1a1a1a; --border-color: #282828; --text-primary: #ffffff; --text-secondary: #a3a3a3; --sent-bg: #22c55e; --received-bg: #1f1f1f; --accent-color: #39ff14; --hover-item: #222222;
        }
        [data-theme="yellow-black"] {
            --bg-color: #0a0a0a; --container-bg: #121212; --header-bg: #1a1a1a; --border-color: #282828; --text-primary: #ffffff; --text-secondary: #a3a3a3; --sent-bg: #ca8a04; --received-bg: #1f1f1f; --accent-color: #ffe600; --hover-item: #222222;
        }
        [data-theme="blue-yellow"] {
            --bg-color: #0f172a; --container-bg: #1e293b; --header-bg: #0f172a; --border-color: #334155; --text-primary: #f8fafc; --text-secondary: #94a3b8; --sent-bg: #00a2ff; --received-bg: #334155; --accent-color: #ffcc00; --hover-item: #3b82f6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-primary); display: flex; justify-content: center; align-items: center; height: 100vh; }
        .container { width: 100%; max-width: 480px; height: 100%; background: var(--container-bg); display: flex; flex-direction: column; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.5); overflow: hidden; }
        @media(min-width: 500px) { .container { height: 92vh; border-radius: 12px; } }
        
        .header { background: var(--header-bg); padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color); min-height: 65px; }
        .header-left { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
        .avatar { width: 40px; height: 40px; background: var(--accent-color); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #111; flex-shrink: 0; overflow: hidden; }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
        .status-info h3 { font-size: 15px; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .status-info p { font-size: 11px; color: var(--text-secondary); }
        .header-btns { display: flex; gap: 4px; flex-shrink: 0; }
        .mods-btn, .status-tab-btn, .back-btn { background: var(--accent-color); color: #111; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 700; }
        
        .bottom-nav { background: var(--header-bg); border-top: 1px solid var(--border-color); display: flex; overflow-x: auto; padding: 6px 4px; gap: 4px; white-space: nowrap; }
        .bottom-nav::-webkit-scrollbar { display: none; }
        .nav-item { background: transparent; border: none; color: var(--text-secondary); padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; transition: 0.2s; flex-shrink: 0; }
        .nav-item:hover, .nav-item.active { background: var(--accent-color); color: #111; }

        .view-section { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .hidden { display: none !important; }
        .chat-list-body { flex: 1; overflow-y: auto; background: var(--container-bg); padding-bottom: 20px; }
        .chat-item { display: flex; align-items: center; padding: 12px 16px; gap: 12px; border-bottom: 1px solid var(--border-color); cursor: pointer; transition: 0.2s; }
        .chat-item:hover { background: var(--hover-item); }
        .chat-item-info { flex: 1; min-width: 0; }
        .chat-item-info h4 { font-size: 14px; color: var(--text-primary); margin-bottom: 3px; display: flex; justify-content: space-between; }
        .chat-item-info h4 span { font-size: 11px; color: var(--text-secondary); font-weight: normal; }
        .chat-item-info p { font-size: 12px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        .fab-btn { position: absolute; bottom: 20px; right: 20px; background: var(--accent-color); color: #111; width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.6); border: none; z-index: 10; font-weight: bold; }
        .radio-fab-btn { position: absolute; bottom: 76px; right: 20px; background: #22c55e; color: #fff; width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.6); border: none; z-index: 10; font-weight: bold; }
        
        .chat-body { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
        .message { max-width: 75%; padding: 8px 12px; border-radius: 8px; font-size: 14px; word-break: break-word; color: var(--text-primary); }
        .message.received { background: var(--received-bg); align-self: flex-start; border: 1px solid var(--border-color); }
        .message.sent { background: var(--sent-bg); align-self: flex-end; color: #fff; }
        .message .time { font-size: 10px; color: var(--text-secondary); float: right; margin-left: 8px; margin-top: 4px; }
        
        .sub-body { flex: 1; padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .download-btn { background: var(--accent-color); color: #111; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; }
        
        .radio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 15px; background: radial-gradient(circle, #1a2228 0%, #0b141a 100%); }
        .cassette { width: 260px; height: 160px; background: linear-gradient(135deg, #2a2f35 0%, #15191d 100%); border: 3px solid var(--accent-color); border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.7); display: flex; flex-direction: column; justify-content: space-between; padding: 12px; position: relative; margin-bottom: 15px; }
        .cassette-label { background: #e2e8f0; color: #0f172a; font-size: 11px; font-weight: bold; padding: 4px 8px; border-radius: 4px; text-align: center; letter-spacing: 1px; }
        .cassette-window { background: #0b141a; border: 2px solid #475569; border-radius: 8px; height: 65px; display: flex; align-items: center; justify-content: space-around; padding: 0 20px; position: relative; }
        .reel { width: 42px; height: 42px; border: 4px dashed #94a3b8; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #1e293b; }
        .reel-center { width: 14px; height: 14px; background: #cbd5e1; border-radius: 50%; }
        .playing-reel { animation: spinReel 2s linear infinite; }
        @keyframes spinReel { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .tape-bridge { position: absolute; bottom: 8px; width: 60px; height: 6px; background: #334155; border-radius: 3px; }

        .volume-control { display: flex; align-items: center; gap: 8px; margin-bottom: 15px; width: 220px; background: var(--header-bg); padding: 8px 12px; border-radius: 20px; border: 1px solid var(--border-color); }
        .volume-control span { font-size: 12px; color: var(--text-secondary); }
        .volume-control input { flex: 1; accent-color: var(--accent-color); cursor: pointer; }

        .radio-btn { background: var(--accent-color); color: #111; border: none; padding: 10px 22px; border-radius: 30px; font-size: 14px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.4); transition: 0.2s; }
        .radio-btn:hover { transform: scale(1.05); }

        .chat-footer { background: var(--header-bg); padding: 10px 16px; display: flex; align-items: center; gap: 8px; border-top: 1px solid var(--border-color); }
        .chat-footer input { flex: 1; background: var(--bg-color); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 8px; color: var(--text-primary); outline: none; font-size: 14px; }
        .chat-footer button { background: var(--accent-color); border: none; color: #111; padding: 10px 14px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: var(--container-bg); padding: 20px; border-radius: 12px; width: 92%; max-width: 420px; border: 1px solid var(--border-color); max-height: 85vh; overflow-y: auto; }
        .modal-content h2 { color: var(--accent-color); margin-bottom: 14px; font-size: 17px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
        .form-group input, .form-group select { width: 100%; background: var(--bg-color); border: 1px solid var(--border-color); padding: 8px; border-radius: 6px; color: var(--text-primary); font-size: 13px; }
        .modal-buttons { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
        .modal-buttons button { padding: 8px 14px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; font-size: 13px; }
        .btn-cancel { background: #334155; color: #cbd5e1; }
        .btn-save { background: var(--accent-color); color: #111; }
    </style>
</head>
<body data-theme="dark-oled" onload="initApp()">
    <div class="container">
        <div class="header">
            <div class="header-left" id="header-left-content">
                <div class="avatar" id="my-avatar">WA</div>
                <div class="status-info">
                    <h3 id="my-name">EnjoyWeb</h3>
                    <p>Online (Evolution API)</p>
                </div>
            </div>
            <div class="header-btns" id="header-buttons">
                <button class="mods-btn" onclick="openMods()" type="button">⚙️ Mods</button>
            </div>
        </div>

        <div id="home-view" class="view-section">
            <div class="chat-list-body" id="chat-list">
                <div style="padding: 30px; text-align: center;">
                    <p style="color: var(--text-secondary); font-size: 13px;">Carregando conversas recentes...</p>
                </div>
            </div>
            <button class="radio-fab-btn" onclick="switchTab('radio', null)" title="Abrir Rádio" type="button">🎧</button>
            <button class="fab-btn" onclick="openContactsModal()" type="button">💬</button>
        </div>

        <div id="friends-view" class="view-section hidden">
            <div class="chat-list-body" id="friends-list">
                <div style="padding: 30px; text-align: center;">
                    <button class="download-btn" onclick="loadFriends()" type="button">👥 Carregar Contatos</button>
                </div>
            </div>
            <button class="radio-fab-btn" onclick="switchTab('radio', null)" title="Abrir Rádio" type="button">🎧</button>
            <button class="fab-btn" onclick="openContactsModal()" type="button">💬</button>
        </div>

        <div id="groups-view" class="view-section hidden">
            <div class="chat-list-body" id="groups-list">
                <div style="padding: 30px; text-align: center;">
                    <button class="download-btn" onclick="loadGroups()" type="button">📢 Carregar Grupos</button>
                </div>
            </div>
            <button class="radio-fab-btn" onclick="switchTab('radio', null)" title="Abrir Rádio" type="button">🎧</button>
            <button class="fab-btn" onclick="openContactsModal()" type="button">💬</button>
        </div>

        <div id="mass-view" class="view-section hidden">
            <div class="sub-body">
                <h3 style="font-size: 15px; color: var(--accent-color);">📢 Disparo em Massa</h3>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Lista de Números (um por linha)</label>
                    <textarea id="mass-numbers" rows="5" style="width:100%; background:var(--bg-color); border:1px solid var(--border-color); color:var(--text-primary); padding:8px; border-radius:6px;"></textarea>
                </div>
                <div class="form-group">
                    <label>Mensagem do Disparo</label>
                    <input type="text" id="mass-text">
                </div>
                <button class="download-btn" onclick="startMassDispatch()" type="button">Iniciar Disparo em Massa</button>
            </div>
            <button class="radio-fab-btn" onclick="switchTab('radio', null)" title="Abrir Rádio" type="button">🎧</button>
        </div>

        <div id="schedule-view" class="view-section hidden">
            <div class="sub-body">
                <h3 style="font-size: 15px; color: var(--accent-color);">⏰ Agendamento de Mensagem</h3>
                <div class="form-group" style="margin-top: 10px;">
                    <label>Número do WhatsApp Destino</label>
                    <input type="text" id="sched-number" placeholder="5543999999999">
                </div>
                <div class="form-group">
                    <label>Mensagem</label>
                    <input type="text" id="sched-text">
                </div>
                <div class="form-group">
                    <label>Atraso em segundos</label>
                    <input type="number" id="sched-delay" value="10">
                </div>
                <button class="download-btn" onclick="scheduleMessage()" type="button">Agendar Disparo</button>
            </div>
            <button class="radio-fab-btn" onclick="switchTab('radio', null)" title="Abrir Rádio" type="button">🎧</button>
        </div>

        <div id="radio-view" class="view-section hidden">
            <div class="radio-container">
                <div class="cassette">
                    <div class="cassette-label">DEFFINE WEB RÁDIO - STEREO</div>
                    <div class="cassette-window">
                        <div class="reel" id="reel-left"><div class="reel-center"></div></div>
                        <div class="tape-bridge"></div>
                        <div class="reel" id="reel-right"><div class="reel-center"></div></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--text-secondary);">
                        <span>SIDE A</span>
                        <span id="radio-status-text">PRONTO</span>
                        <span>HI-FI</span>
                    </div>
                </div>

                <div class="volume-control">
                    <span>🔊 Vol</span>
                    <input type="range" id="volume-slider" min="0" max="1" step="0.05" value="1" oninput="changeVolume(this.value)">
                </div>

                <audio id="web-radio-audio" src="https://azuracast.deffine.com.br/listen/deffine_web_radio/radio.mp3"></audio>
                <div style="display:flex; gap:10px;">
                    <button class="radio-btn" id="radio-toggle-btn" onclick="toggleRadio()" type="button">▶️ OUVIR</button>
                    <button class="radio-btn" style="background:#ef4444; color:#fff;" onclick="stopRadio()" type="button">⏹️ DESLIGAR</button>
                </div>
            </div>
        </div>

        <div id="chat-view" class="view-section hidden">
            <div class="chat-body" id="chat-body"></div>
            <div class="chat-footer">
                <input type="text" id="message-input" placeholder="Digite uma mensagem...">
                <button onclick="sendMessage()" type="button">Enviar</button>
            </div>
        </div>

        <div class="bottom-nav">
            <button class="nav-item active" onclick="switchTab('home', this)" type="button">🏠 Início</button>
            <button class="nav-item" onclick="switchTab('friends', this)" type="button">👥 Amigos</button>
            <button class="nav-item" onclick="switchTab('groups', this)" type="button">📢 Grupos</button>
            <button class="nav-item" onclick="switchTab('mass', this)" type="button">🚀 Disparo</button>
            <button class="nav-item" onclick="switchTab('schedule', this)" type="button">⏰ Agenda</button>
        </div>
    </div>

    <div class="modal" id="contacts-modal">
        <div class="modal-content">
            <h2>👥 Iniciar Conversa</h2>
            <div class="form-group">
                <input type="text" id="contact-search-input" oninput="filterContacts()" placeholder="Pesquisar...">
            </div>
            <div id="contacts-modal-list" style="max-height: 300px; overflow-y: auto;"></div>
            <div class="modal-buttons">
                <button class="btn-cancel" onclick="closeContactsModal()" type="button">Fechar</button>
            </div>
        </div>
    </div>

    <div class="modal" id="mods-modal">
        <div class="modal-content">
            <h2>⚙️ Painel GB Mods</h2>
            <div class="form-group">
                <label>Tema e Cores</label>
                <select id="theme-select">
                    <option value="dark-oled">Preto OLED (Padrão)</option>
                    <option value="light">Claro</option>
                    <option value="lime-black">Verde Limão com Preto</option>
                    <option value="yellow-black">Amarelo com Preto</option>
                    <option value="blue-yellow">Azul com Amarelo</option>
                </select>
            </div>
            <div class="form-group">
                <label>API OpenAI Key</label>
                <input type="password" id="api-key">
            </div>
            <div class="modal-buttons">
                <button class="btn-cancel" onclick="closeMods()" type="button">Cancelar</button>
                <button class="btn-save" onclick="saveMods()" type="button">Salvar</button>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        let currentChatName = '';
        let activeTabName = 'home';
        let allContactsCache = [];

        function initApp() {
            refreshData();
            loadProfileInfo();
        }

        function loadProfileInfo() {
            fetch('/get_profile')
                .then(res => res.json())
                .then(data => {
                    if (data.name) {
                        document.getElementById('my-name').innerText = data.name;
                    }
                    if (data.pic) {
                        document.getElementById('my-avatar').innerHTML = '<img src="' + data.pic + '" alt="Perfil">';
                    }
                }).catch(e => console.error(e));
        }

        function switchTab(tab, btnElement) {
            activeTabName = tab;
            document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.nav-item').forEach(el => {
                if(el !== btnElement) el.classList.remove('active');
            });
            if(btnElement) btnElement.classList.add('active');

            document.getElementById('header-buttons').innerHTML = '<button class="mods-btn" onclick="openMods()" type="button">⚙️ Mods</button>';

            if (tab === 'home') { document.getElementById('home-view').classList.remove('hidden'); refreshData(); }
            else if (tab === 'friends') { document.getElementById('friends-view').classList.remove('hidden'); loadFriends(); }
            else if (tab === 'groups') { document.getElementById('groups-view').classList.remove('hidden'); loadGroups(); }
            else if (tab === 'mass') document.getElementById('mass-view').classList.remove('hidden');
            else if (tab === 'schedule') document.getElementById('schedule-view').classList.remove('hidden');
            else if (tab === 'radio') document.getElementById('radio-view').classList.remove('hidden');
        }

        function openChatDirect(id, name, pic) {
            currentChatId = id;
            currentChatName = name;
            let avatarHTML = pic ? '<img src="' + pic + '" alt="Avatar">' : name.substring(0,2).toUpperCase();
            
            document.getElementById('header-left-content').innerHTML = `
                <div class="avatar">` + avatarHTML + `</div>
                <div class="status-info">
                    <h3>` + name + `</h3>
                    <p>` + id + `</p>
                </div>`;
            
            document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
            document.getElementById('chat-view').classList.remove('hidden');
            document.getElementById('header-buttons').innerHTML = '<button class="back-btn" onclick="switchTab(\\'' + activeTabName + '\\', null)" type="button">⬅️ Voltar</button>';
            loadMessages(id);
        }

        function refreshData() {
            fetch('/get_chats')
                .then(res => res.json())
                .then(data => {
                    if(data.theme) document.body.setAttribute('data-theme', data.theme);
                    renderChatList(data.chats);
                }).catch(e => console.error(e));
        }

        function renderChatList(chats) {
            const listContainer = document.getElementById('chat-list');
            listContainer.innerHTML = '';
            if (!chats || chats.length === 0) {
                listContainer.innerHTML = '<div style="padding: 30px; text-align: center;"><p style="color: var(--text-secondary); font-size: 13px; margin-bottom: 15px;">Nenhuma conversa recente encontrada.</p></div>';
                return;
            }
            chats.forEach(chat => {
                let avatarHTML = chat.pic ? '<img src="' + chat.pic + '">' : chat.name.substring(0,2).toUpperCase();
                let item = document.createElement('div');
                item.className = 'chat-item';
                item.onclick = () => openChatDirect(chat.id, chat.name, chat.pic);
                item.innerHTML = '<div class="avatar">' + avatarHTML + '</div><div class="chat-item-info"><h4>' + chat.name + ' <span>' + (chat.time || '') + '</span></h4><p>' + chat.last_msg + '</p></div>';
                listContainer.appendChild(item);
            });
        }

        function loadFriends() {
            const container = document.getElementById('friends-list');
            container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Carregando contatos...</div>';
            fetch('/get_contacts')
                .then(res => res.json())
                .then(data => {
                    container.innerHTML = '';
                    const contacts = data.contacts || [];
                    if(contacts.length === 0) {
                        container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Nenhum contato encontrado.</div>';
                        return;
                    }
                    contacts.forEach(c => {
                        let avatarHTML = c.pic ? '<img src="' + c.pic + '">' : c.name.substring(0,2).toUpperCase();
                        let item = document.createElement('div');
                        item.className = 'chat-item';
                        item.onclick = () => openChatDirect(c.id, c.name, c.pic);
                        item.innerHTML = '<div class="avatar">' + avatarHTML + '</div><div class="chat-item-info"><h4>' + c.name + '</h4><p>' + c.id + '</p></div>';
                        container.appendChild(item);
                    });
                });
        }

        function loadGroups() {
            const container = document.getElementById('groups-list');
            container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Carregando grupos...</div>';
            fetch('/get_groups')
                .then(res => res.json())
                .then(data => {
                    container.innerHTML = '';
                    const groups = data.groups || [];
                    if(groups.length === 0) {
                        container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">Nenhum grupo encontrado.</div>';
                        return;
                    }
                    groups.forEach(g => {
                        let avatarHTML = g.pic ? '<img src="' + g.pic + '">' : g.name.substring(0,2).toUpperCase();
                        let item = document.createElement('div');
                        item.className = 'chat-item';
                        item.onclick = () => openChatDirect(g.id, g.name, g.pic);
                        item.innerHTML = '<div class="avatar">' + avatarHTML + '</div><div class="chat-item-info"><h4>' + g.name + '</h4><p>' + g.id + '</p></div>';
                        container.appendChild(item);
                    });
                });
        }

        function openContactsModal() {
            document.getElementById('contacts-modal').style.display = 'flex';
            fetch('/get_contacts')
                .then(res => res.json())
                .then(data => {
                    allContactsCache = data.contacts || [];
                    renderContactModalList(allContactsCache);
                });
        }

        function closeContactsModal() { document.getElementById('contacts-modal').style.display = 'none'; }

        function filterContacts() {
            const query = document.getElementById('contact-search-input').value.toLowerCase();
            const filtered = allContactsCache.filter(c => c.name.toLowerCase().includes(query) || c.id.toLowerCase().includes(query));
            renderContactModalList(filtered);
        }

        function renderContactModalList(contacts) {
            const container = document.getElementById('contacts-modal-list');
            container.innerHTML = '';
            contacts.forEach(c => {
                let avatarHTML = c.pic ? '<img src="' + c.pic + '">' : c.name.substring(0,2).toUpperCase();
                let item = document.createElement('div');
                item.className = 'chat-item';
                item.onclick = () => { closeContactsModal(); openChatDirect(c.id, c.name, c.pic); };
                item.innerHTML = '<div class="avatar">' + avatarHTML + '</div><div class="chat-item-info"><h4>' + c.name + '</h4><p>' + c.id + '</p></div>';
                container.appendChild(item);
            });
        }

        function loadMessages(chatId) {
            fetch('/get_messages?chat_id=' + encodeURIComponent(chatId))
                .then(res => res.json())
                .then(data => {
                    const chatBody = document.getElementById('chat-body');
                    chatBody.innerHTML = '';
                    (data.messages || []).forEach(msg => {
                        let div = document.createElement('div');
                        div.className = 'message ' + (msg.is_me ? 'sent' : 'received');
                        div.innerHTML = '<span>' + msg.text + '</span><span class="time">' + msg.time + '</span>';
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
            }).then(() => { input.value = ''; loadMessages(currentChatId); });
        }

        function toggleRadio() {
            const audio = document.getElementById('web-radio-audio');
            const btn = document.getElementById('radio-toggle-btn');
            const reelLeft = document.getElementById('reel-left');
            const reelRight = document.getElementById('reel-right');
            const statusTxt = document.getElementById('radio-status-text');

            if (audio.paused) {
                audio.play().then(() => {
                    btn.innerText = '⏸️ PAUSAR';
                    reelLeft.classList.add('playing-reel');
                    reelRight.classList.add('playing-reel');
                    statusTxt.innerText = 'AO VIVO';
                }).catch(e => alert('Erro ao reproduzir rádio: ' + e));
            } else {
                audio.pause();
                btn.innerText = '▶️ OUVIR';
                reelLeft.classList.remove('playing-reel');
                reelRight.classList.remove('playing-reel');
                statusTxt.innerText = 'PAUSADO';
            }
        }

        function stopRadio() {
            const audio = document.getElementById('web-radio-audio');
            const btn = document.getElementById('radio-toggle-btn');
            const reelLeft = document.getElementById('reel-left');
            const reelRight = document.getElementById('reel-right');
            const statusTxt = document.getElementById('radio-status-text');

            audio.pause();
            audio.currentTime = 0;
            btn.innerText = '▶️ OUVIR';
            reelLeft.classList.remove('playing-reel');
            reelRight.classList.remove('playing-reel');
            statusTxt.innerText = 'DESLIGADO';
        }

        function changeVolume(val) {
            const audio = document.getElementById('web-radio-audio');
            audio.volume = val;
        }

        function scheduleMessage() {
            const number = document.getElementById('sched-number').value.trim();
            const text = document.getElementById('sched-text').value;
            const delay = document.getElementById('sched-delay').value;
            if(!number || !text) return alert('Preencha os campos!');
            fetch('/schedule_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ chat_id: number, text: text, delay_seconds: parseInt(delay) })
            }).then(res => res.json()).then(data => alert(data.status));
        }

        function startMassDispatch() {
            const raw = document.getElementById('mass-numbers').value.trim();
            const text = document.getElementById('mass-text').value.trim();
            if(!raw || !text) return alert('Preencha os campos!');
            const numbers = raw.split(/[\\n,]+/).map(n => n.trim()).filter(n => n);
            fetch('/mass_dispatch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ numbers: numbers, text: text })
            }).then(() => alert('Disparo concluído!'));
        }

        function openMods() {
            fetch('/get_settings')
                .then(res => res.json())
                .then(settings => {
                    document.getElementById('theme-select').value = settings.theme;
                    document.getElementById('api-key').value = settings.openai_api_key;
                    document.getElementById('mods-modal').style.display = 'flex';
                });
        }

        function closeMods() { document.getElementById('mods-modal').style.display = 'none'; }

        function saveMods() {
            const settings = {
                theme: document.getElementById('theme-select').value,
                openai_api_key: document.getElementById('api-key').value,
                ai_enabled: false,
                auto_reply_enabled: false,
                auto_reply_text: "",
                lossless_media: true,
                anti_revoke: true,
                freeze_last_seen: true,
                anti_blue_tick: true,
                ghost_mode: true
            };
            fetch('/save_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            }).then(() => { closeMods(); location.reload(); });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_TEMPLATE

@app.get("/get_profile")
def get_profile():
    name = INSTANCE_NAME
    pic = ""
    try:
        url_pic = f"{EVOLUTION_URL}/chat/fetchProfilePictureUrl/{INSTANCE_NAME}?number={INSTANCE_NAME}"
        res_pic = requests.get(url_pic, headers=headers, timeout=2)
        if res_pic.status_code != 200:
            res_pic = requests.post(f"{EVOLUTION_URL}/chat/fetchProfilePictureUrl/{INSTANCE_NAME}", json={"number": INSTANCE_NAME}, headers=headers, timeout=2)
            
        if res_pic.status_code == 200:
            data = res_pic.json()
            pic = data.get("profilePictureUrl") or data.get("pictureUrl") or data.get("url") or ""
    except Exception:
        pass
    return {"name": name, "pic": pic}

@app.get("/get_chats")
def get_chats():
    chats_list = []
    try:
        url = f"{EVOLUTION_URL}/chat/findChats/{INSTANCE_NAME}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            response = requests.post(url, json={}, headers=headers, timeout=5)
            
        if response.status_code == 200:
            data = response.json()
            items = data if isinstance(data, list) else (data.get("chats") or data.get("records") or data.get("data") or [])
            for c in items:
                jid = c.get("id") or c.get("remoteJid", "")
                if not jid: continue
                name = c.get("name") or c.get("pushName") or jid.split("@")[0]
                
                pic = c.get("profilePictureUrl") or c.get("pictureUrl") or c.get("imageUrl") or ""

                last_message = c.get("lastMessage", {})
                last_text = last_message.get("conversation") or last_message.get("text") or "Conversa ativa"
                timestamp = last_message.get("messageTimestamp", 0)
                time_str = datetime.fromtimestamp(int(timestamp)).strftime("%H:%M") if timestamp else ""
                chats_list.append({"id": jid, "name": name, "last_msg": last_text, "pic": pic, "time": time_str})
    except Exception as e:
        print(f"Erro chats: {e}")
    return {"chats": chats_list, "theme": gb_settings["theme"]}

@app.get("/get_contacts")
def get_contacts():
    contacts_list = []
    try:
        url = f"{EVOLUTION_URL}/chat/findContacts/{INSTANCE_NAME}"
        res = requests.post(url, json={}, headers=headers, timeout=5)
        if res.status_code != 200:
            res = requests.get(url, headers=headers, timeout=5)
            
        if res.status_code == 200:
            data = res.json()
            items = data if isinstance(data, list) else (data.get("contacts") or data.get("records") or data.get("data") or [])
            for c in items:
                jid = c.get("id") or c.get("remoteJid", "")
                name = c.get("name") or c.get("pushName") or jid.split("@")[0]
                
                pic = c.get("profilePictureUrl") or c.get("pictureUrl") or c.get("imageUrl") or ""

                contacts_list.append({"id": jid, "name": name, "pic": pic})
    except Exception as e:
        print(f"Erro contatos: {e}")
    return {"contacts": contacts_list}

@app.get("/get_groups")
def get_groups():
    groups_list = []
    try:
        url = f"{EVOLUTION_URL}/group/fetchAllGroups/{INSTANCE_NAME}?getParticipants=false"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            items = data if isinstance(data, list) else (data.get("groups") or [])
            for g in items:
                jid = g.get("id") or g.get("Jid", "")
                name = g.get("subject") or g.get("name", "Grupo WhatsApp")
                pic = g.get("pictureUrl") or g.get("profilePictureUrl", "")
                groups_list.append({"id": jid, "name": name, "pic": pic})
    except Exception as e:
        print(f"Erro grupos: {e}")
    return {"groups": groups_list}

@app.get("/get_messages")
def get_messages(chat_id: str):
    msgs = []
    seen_ids = set()
    try:
        url = f"{EVOLUTION_URL}/chat/findMessages/{INSTANCE_NAME}"
        payload = {"where": {"remoteJid": chat_id}}
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                messages_data = []
                if isinstance(data, list):
                    messages_data = data
                elif isinstance(data, dict):
                    msg_container = data.get("messages")
                    if isinstance(msg_container, dict):
                        messages_data = msg_container.get("records", []) or []
                    elif isinstance(msg_container, list):
                        messages_data = msg_container

                for m in messages_data:
                    if not isinstance(m, dict):
                        continue
                    
                    # Filtro de segurança: Garante que a mensagem pertence realmente a este chat
                    remote_jid = m.get("remoteJid") or m.get("key", {}).get("remoteJid", "")
                    if remote_jid and remote_jid != chat_id:
                        continue

                    # Evita mensagens duplicadas na tela
                    msg_id = m.get("id") or m.get("key", {}).get("id", "")
                    if msg_id and msg_id in seen_ids:
                        continue
                    if msg_id:
                        seen_ids.add(msg_id)

                    msg_obj = m.get("message") or {}
                    body = msg_obj.get("conversation") or msg_obj.get("extendedTextMessage", {}).get("text") or "[Mídia]"
                    key_obj = m.get("key") or {}
                    from_me = key_obj.get("fromMe", False)
                    timestamp = m.get("messageTimestamp", 0)
                    time_str = datetime.fromtimestamp(int(timestamp)).strftime("%H:%M") if timestamp else ""
                    msgs.append({"text": str(body), "is_me": from_me, "time": time_str})
    except Exception as e:
        print(f"Erro msgs: {e}")
    return {"messages": msgs}

@app.post("/send_message")
def send_message(data: MessageModel):
    try:
        url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
        payload = {"number": data.chat_id, "text": data.text, "delay": 1200}
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        return {"status": "success", "response": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/mass_dispatch")
def mass_dispatch(data: MassModel):
    dict_data = data.dict() if hasattr(data, 'dict') else data.model_dump()
    try:
        for num in dict_data.get("numbers", []):
            url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
            payload = {"number": num, "text": dict_data.get("text"), "delay": 1200}
            requests.post(url, json=payload, headers=headers, timeout=5)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/schedule_message")
async def schedule_message(data: ScheduleModel):
    async def delayed_task():
        await asyncio.sleep(data.delay_seconds)
        try:
            url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
            payload = {"number": data.chat_id, "text": data.text, "delay": 1200}
            requests.post(url, json=payload, headers=headers, timeout=5)
        except Exception as e:
            print(f"Erro agendamento: {e}")
    asyncio.create_task(delayed_task())
    return {"status": f"Mensagem agendada para daqui a {data.delay_seconds} segundos!"}

@app.get("/get_settings")
def get_settings():
    return gb_settings

@app.post("/save_settings")
def save_settings(data: SettingsModel):
    gb_settings.update(data.dict() if hasattr(data, 'dict') else data.model_dump())
    return {"status": "success"}
