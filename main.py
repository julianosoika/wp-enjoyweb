from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()
SENHA = "123456"

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
        <h2>Bem-vindo ⚡</h2>
        <p>Digite sua senha para entrar.</p>
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
    
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp GB Custom v10</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400,500;600&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { height: 100vh; overflow: hidden; background: #0b141a; color: #e9edef; font-family: 'Plus Jakarta Sans', sans-serif; }
        .app-container { display: flex; width: 100vw; height: 100vh; position: relative; }
        .sidebar { width: 380px; background: #111b21; border-right: 1px solid #222d34; display: flex; flex-direction: column; height: 100%; flex-shrink: 0; }
        .sidebar-header { padding: 15px 20px; background: #202c33; display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 15px; color: #34d399; }
        .gb-badge { background: rgba(52,211,153,0.15); color: #34d399; font-size: 11px; padding: 4px 8px; border-radius: 6px; }
        .contact-list { overflow-y: auto; flex: 1; }
        .contact { padding: 15px 20px; display: flex; align-items: center; gap: 15px; border-bottom: 1px solid #222d34; cursor: pointer; }
        .contact:hover, .contact.active { background: #202c33; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; background: #00a884; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; flex-shrink: 0; }
        .chat-area { flex: 1; display: flex; flex-direction: column; background: #0b141a; height: 100%; }
        .chat-header { padding: 12px 20px; background: #202c33; border-bottom: 1px solid #222d34; display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background-image: radial-gradient(#222d34 1px, transparent 1px); background-size: 20px 20px; }
        .msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 14px; line-height: 1.4; word-break: break-word; }
        .received { background: #202c33; align-self: flex-start; }
        .sent { background: #005c4b; align-self: flex-end; }
        .chat-input { padding: 15px 20px; background: #202c33; display: flex; gap: 15px; align-items: center; flex-shrink: 0; }
        .chat-input input { flex: 1; padding: 12px 16px; background: #2a3942; border: none; border-radius: 8px; color: #fff; font-size: 14px; }
        .chat-input input:focus { outline: none; }
        a.logout { color: #ef4444; text-decoration: none; font-size: 13px; font-weight: 600; padding: 6px 12px; background: rgba(239,68,68,0.1); border-radius: 6px; }
        #backBtn { display: none; }

        @media (max-width: 768px) {
            .app-container:not(.mobile-active) .chat-area { display: none !important; }
            .app-container.mobile-active .sidebar { display: none !important; }
            .app-container.mobile-active .chat-area { display: flex !important; width: 100% !important; position: absolute; top: 0; left: 0; z-index: 99; height: 100%; }
            .sidebar { width: 100% !important; }
            #backBtn { display: inline-block !important; }
        }
    </style>
</head>
<body>
    <div class="app-container" id="appBox">
        <div class="sidebar">
            <div class="sidebar-header">
                <span>💬 WhatsApp GB</span>
                <span class="gb-badge">PRO v10</span>
            </div>
            <div class="contact-list">
                <div class="contact" onclick="openChat()">
                    <div class="avatar">JS</div>
                    <div style="overflow:hidden">
                        <h4>Cliente Exemplo</h4>
                        <p style="font-size:12px;color:#8696a0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">Olá, tudo bem?</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="chat-area">
            <div class="chat-header">
                <div style="display:flex;align-items:center;gap:12px;">
                    <button id="backBtn" style="background:none;border:none;color:#34d399;font-size:20px;cursor:pointer;margin-right:5px;" onclick="closeChat()">⬅</button>
                    <div class="avatar" style="width:35px;height:35px;font-size:14px;">JS</div>
                    <span style="font-weight:600">Cliente Exemplo</span>
                </div>
                <a href="/" class="logout">Sair</a>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="msg received">Olá! Seja bem-vindo ao painel customizado estilo WhatsApp GB.</div>
                <div class="msg sent">Incrível! As funções avançadas vão entrar em breve aqui.</div>
            </div>
            <div class="chat-input">
                <input type="text" id="msgInput" placeholder="Digite uma mensagem" onkeypress="handleKey(event)">
                <button style="background:#00a884;color:#fff;border:none;padding:12px 20px;border-radius:8px;font-weight:600;cursor:pointer" onclick="sendMsg()">Enviar</button>
            </div>
        </div>
    </div>

    <script>
        function openChat() {
            document.getElementById('appBox').classList.add('mobile-active');
            document.querySelector('.contact').classList.add('active');
        }

        function closeChat() {
            document.getElementById('appBox').classList.remove('mobile-active');
        }

        function sendMsg() {
            const input = document.getElementById('msgInput');
            const txt = input.value.trim();
            if(!txt) return;
            const container = document.getElementById('chatMessages');
            const div = document.createElement('div');
            div.className = 'msg sent';
            div.textContent = txt;
            container.appendChild(div);
            input.value = '';
            container.scrollTop = container.scrollHeight;
        }

        function handleKey(e) {
            if(e.key === 'Enter') {
                sendMsg();
            }
        }
    </script>
</body>
</html>"""