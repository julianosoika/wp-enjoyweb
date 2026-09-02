from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import httpx

app = FastAPI()
SENHA = "123456"

# Armazenamento em memória simples para configurações e chat dinâmico
CONFIG = {
    "openai_key": "",
    "ai_enabled": False,
    "theme": "dark"
}

@app.get("/", response_class=HTMLResponse)
def login_page():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Login - WhatsApp GB</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body { background: #07090e; color: #fff; font-family: 'Plus Jakarta Sans', sans-serif; display: flex; height: 100vh; align-items: center; justify-content: center; margin: 0; }
        .card { background: #1e293b; padding: 40px; border-radius: 20px; width: 100%; max-width: 380px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.05); }
        h2 { margin-bottom: 8px; color: #34d399; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; background: #0f172a; border: 1px solid #334155; border-radius: 10px; color: #fff; margin-bottom: 15px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #10b981; border: none; border-radius: 10px; color: #fff; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="card">
        <h2>WhatsApp GB PRO ⚡</h2>
        <p>Digite sua senha para acessar o painel.</p>
        <form action="/login" method="POST">
            <input type="password" name="p" placeholder="Sua senha" required>
            <button type="submit">Acessar Painel</button>
        </form>
    </div>
</body>
</html>"""

@app.post("/login")
def login_submit(p: str = Form(...)):
    if p == SENHA:
        response = RedirectResponse(url="/dash", status_code=303)
        response.set_cookie(key="ok", value="1")
        return response
    return RedirectResponse(url="/", status_code=303)

@app.get("/dash", response_class=HTMLResponse)
def dashboard(request: Request):
    if request.cookies.get("ok") != "1":
        return RedirectResponse(url="/", status_code=303)
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp GB Custom v11</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400,500;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html, body {{ height: 100vh; overflow: hidden; background: #0b141a; color: #e9edef; font-family: 'Plus Jakarta Sans', sans-serif; }}
        .app-container {{ display: flex; width: 100vw; height: 100vh; position: relative; }}
        .sidebar {{ width: 380px; background: #111b21; border-right: 1px solid #222d34; display: flex; flex-direction: column; height: 100%; flex-shrink: 0; }}
        .sidebar-header {{ padding: 15px 20px; background: #202c33; display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 15px; color: #34d399; }}
        .gb-badge {{ background: rgba(52,211,153,0.15); color: #34d399; font-size: 11px; padding: 4px 8px; border-radius: 6px; cursor: pointer; }}
        .contact-list {{ overflow-y: auto; flex: 1; }}
        .contact {{ padding: 15px 20px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid #222d34; cursor: pointer; }}
        .contact:hover, .contact.active {{ background: #202c33; }}
        .avatar {{ width: 40px; height: 40px; border-radius: 50%; background: #00a884; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; flex-shrink: 0; }}
        .chat-area {{ flex: 1; display: flex; flex-direction: column; background: #0b141a; height: 100%; }}
        .chat-header {{ padding: 12px 20px; background: #202c33; border-bottom: 1px solid #222d34; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }}
        .chat-messages {{ flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background-image: radial-gradient(#222d34 1px, transparent 1px); background-size: 20px 20px; }}
        .msg {{ max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 14px; line-height: 1.4; word-break: break-word; }}
        .received {{ background: #202c33; align-self: flex-start; }}
        .sent {{ background: #005c4b; align-self: flex-end; }}
        .chat-input {{ padding: 15px 20px; background: #202c33; display: flex; gap: 15px; align-items: center; flex-shrink: 0; }}
        .chat-input input {{ flex: 1; padding: 12px 16px; background: #2a3942; border: none; border-radius: 8px; color: #fff; font-size: 14px; }}
        .chat-input input:focus {{ outline: none; }}
        a.logout {{ color: #ef4444; text-decoration: none; font-size: 13px; font-weight: 600; padding: 6px 12px; background: rgba(239,68,68,0.1); border-radius: 6px; }}
        #backBtn {{ display: none; }}

        /* Modal GB Settings */
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 999; justify-content: center; align-items: center; }}
        .modal-content {{ background: #1f2c34; padding: 25px; border-radius: 12px; width: 90%; max-width: 400px; border: 1px solid #2a3942; }}
        .modal-content h3 {{ color: #34d399; margin-bottom: 15px; }}
        .modal-content label {{ display: block; font-size: 13px; color: #8696a0; margin-bottom: 5px; }}
        .modal-content input, .modal-content select {{ width: 100%; padding: 10px; background: #2a3942; border: 1px solid #3d4a52; border-radius: 6px; color: #fff; margin-bottom: 15px; }}
        .modal-buttons {{ display: flex; justify-content: flex-end; gap: 10px; }}
        .btn-save {{ background: #00a884; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
        .btn-close {{ background: #3d4a52; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }}

        @media (max-width: 768px) {{
            .app-container:not(.mobile-active) .chat-area {{ display: none !important; }}
            .app-container.mobile-active .sidebar {{ display: none !important; }}
            .app-container.mobile-active .chat-area {{ display: flex !important; width: 100% !important; position: absolute; top: 0; left: 0; z-index: 99; height: 100%; }}
            .sidebar {{ width: 100% !important; }}
            #backBtn {{ display: inline-block !important; }}
        }}
    </style>
</head>
<body>
    <div class="app-container" id="appBox">
        <div class="sidebar">
            <div class="sidebar-header">
                <span>💬 WhatsApp GB</span>
                <span class="gb-badge" onclick="openSettings()">⚙️ GB Mods</span>
            </div>
            <div class="contact-list">
                <div class="contact" onclick="openChat()">
                    <div class="avatar">IA</div>
                    <div style="overflow:hidden">
                        <h4>Assistente ChatGPT (GB)</h4>
                        <p style="font-size:12px;color:#8696a0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" id="lastMsgPreview">Clique para conversar com a IA...</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="chat-area">
            <div class="chat-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <button id="backBtn" style="background:none;border:none;color:#34d399;font-size:20px;cursor:pointer;margin-right:5px;" onclick="closeChat()">⬅</button>
                    <div class="avatar" style="width:35px;height:35px;font-size:14px;">IA</div>
                    <div>
                        <span style="font-weight:600;display:block">Assistente ChatGPT</span>
                        <span style="font-size:11px;color:#34d399;" id="aiStatusIndicator">Modo IA: Desativado (Configure a API)</span>
                    </div>
                </div>
                <a href="/" class="logout">Sair</a>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="msg received">Olá! Sou o seu Assistente com IA integrado via WhatsApp GB v11. Vá em 'GB Mods' ⚙️ para colocar sua chave da OpenAI e ativar minhas respostas automáticas inteligentes!</div>
            </div>
            <div class="chat-input">
                <input type="text" id="msgInput" placeholder="Digite uma mensagem para a IA..." onkeypress="handleKey(event)">
                <button style="background:#00a884;color:#fff;border:none;padding:12px 20px;border-radius:8px;font-weight:600;cursor:pointer" onclick="sendMsg()">Enviar</button>
            </div>
        </div>
    </div>

    <!-- Modal de Configurações GB -->
    <div class="modal" id="settingsModal">
        <div class="modal-content">
            <h3>⚙️ Configurações GB & IA</h3>
            <label>Chave da API OpenAI (ChatGPT)</label>
            <input type="password" id="apiKeyInput" placeholder="sk-..." value="{CONFIG['openai_key']}">
            
            <label>Status da Inteligência Artificial</label>
            <select id="aiToggle">
                <option value="false" {'selected' if not CONFIG['ai_enabled'] else ''}>Desativado</option>
                <option value="true" {'selected' if CONFIG['ai_enabled'] else ''}>Ativado (ChatGPT Respondendo)</option>
            </select>

            <div class="modal-buttons">
                <button class="btn-close" onclick="closeSettings()">Cancelar</button>
                <button class="btn-save" onclick="saveSettings()">Salvar Configurações</button>
            </div>
        </div>
    </div>

    <script>
        let aiActive = {'true' if CONFIG['ai_enabled'] else 'false'};

        function openChat() {{
            document.getElementById('appBox').classList.add('mobile-active');
            document.querySelector('.contact').classList.add('active');
        }}

        function closeChat() {{
            document.getElementById('appBox').classList.remove('mobile-active');
        }}

        function openSettings() {{
            document.getElementById('settingsModal').style.display = 'flex';
        }}

        function closeSettings() {{
            document.getElementById('settingsModal').style.display = 'none';
        }}

        async function saveSettings() {{
            const key = document.getElementById('apiKeyInput').value;
            const enabled = document.getElementById('aiToggle').value;

            const res = await fetch('/api/settings', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ openai_key: key, ai_enabled: enabled === 'true' }})
            }});

            if(res.ok) {{
                aiActive = (enabled === 'true');
                updateAiStatusUI();
                closeSettings();
                alert('Configurações GB salvas com sucesso!');
            }} else {{
                alert('Erro ao salvar configurações.');
            }}
        }}

        function updateAiStatusUI() {{
            const indicator = document.getElementById('aiStatusIndicator');
            if(aiActive) {{
                indicator.textContent = 'Modo IA: Ativo ⚡ (ChatGPT)';
                indicator.style.color = '#34d399';
            }} else {{
                indicator.textContent = 'Modo IA: Desativado';
                indicator.style.color = '#8696a0';
            }}
        }}

        async function sendMsg() {{
            const input = document.getElementById('msgInput');
            const txt = input.value.trim();
            if(!txt) return;

            const container = document.getElementById('chatMessages');
            
            // Adiciona mensagem do usuário
            const userDiv = document.createElement('div');
            userDiv.className = 'msg sent';
            userDiv.textContent = txt;
            container.appendChild(userDiv);
            
            input.value = '';
            container.scrollTop = container.scrollHeight;
            document.getElementById('lastMsgPreview').textContent = txt;

            // Envia para o backend processar (IA ou eco simulado)
            try {{
                const response = await fetch('/api/chat', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message: txt }})
                }};
                
                const data = await response.json();
                
                const botDiv = document.createElement('div');
                botDiv.className = 'msg received';
                botDiv.textContent = data.reply;
                container.appendChild(botDiv);
                container.scrollTop = container.scrollHeight;
                document.getElementById('lastMsgPreview').textContent = data.reply;

            }} catch (err) {{
                console.error(err);
            }}
        }}

        function handleKey(e) {{
            if(e.key === 'Enter') {{
                sendMsg();
            }}
        }}

        updateAiStatusUI();
    </script>
</body>
</html>"""

@app.post("/api/settings")
async def update_settings(request: Request):
    data = await request.json()
    CONFIG["openai_key"] = data.get("openai_key", "")
    CONFIG["ai_enabled"] = data.get("ai_enabled", False)
    return {"status": "success"}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")

    # Se a IA estiver ativada e houver chave da OpenAI configurada
    if CONFIG["ai_enabled"] and CONFIG["openai_key"]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {CONFIG['openai_key']}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "Você é um assistente virtual inteligente integrado a um painel de WhatsApp GB customizado."},
                        {"role": "user", "content": user_msg}
                    ]
                }
                response = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                if response.status_code == 200:
                    res_json = response.json()
                    reply = res_json["choices"][0]["message"]["content"]
                    return {"reply": reply}
                else:
                    return {"reply": f"[Erro na API da OpenAI]: {response.text}"}
        except Exception as e:
            return {"reply": f"[Erro de conexão com ChatGPT]: {str(e)}"}
    
    # Comportamento padrão caso a IA não esteja ativa
    if CONFIG["ai_enabled"] and not CONFIG["openai_key"]:
        return {"reply": "A IA está ativada, mas você esqueceu de preencher a chave da API OpenAI em 'GB Mods' ⚙️!"}
    
    return {"reply": f"Mensagem recebida (Modo Simulado GB): '{user_msg}'. Ative o ChatGPT no menu 'GB Mods' para respostas inteligentes reais!"}