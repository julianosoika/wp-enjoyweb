from datetime import datetime
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Configurações e Estado do GB Mods
gb_settings = {
    "openai_api_key": "",
    "ai_enabled": False,
    "anti_revoke": True,  # Anti-apagar mensagem ativado por padrão
    "freeze_last_seen": True,  # Congelar visto por último
    "anti_blue_tick": True,  # Ocultar confirmação de leitura
    "ghost_mode": True,  # Ocultar "digitando..."
}

# Banco de dados simulado para as mensagens
mensagens = [
    {
        "id": 1,
        "sender": "Assistente WhatsApp GB",
        "text": "Bem-vindo ao WhatsApp GB Custom! Configure suas opções no menu 'GB Mods'.",
        "time": "00:00",
        "is_me": False,
        "revoked": False,
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp GB Custom v12</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0b141a; color: #e9edef; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .container { width: 100%; max-width: 480px; height: 100%; background: #111b21; display: flex; flex-direction: column; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        @media(min-width: 500px) { .container { height: 90vh; border-radius: 10px; } }
        
        /* Header */
        .header { background: #202c33; padding: 10px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2f3b43; }
        .header-left { display: flex; align-items: center; gap: 12px; }
        .avatar { width: 40px; height: 40px; background: #00a884; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; }
        .status-info h3 { font-size: 16px; color: #e9edef; }
        .status-info p { font-size: 12px; color: #8696a0; }
        .mods-btn { background: #005c4b; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; }
        .mods-btn:hover { background: #008069; }

        /* Chat Body */
        .chat-body { flex: 1; padding: 16px; overflow-y: auto; background-image: radial-gradient(#1f2c34 1px, transparent 1px); background-size: 20px 20px; display: flex; flex-direction: column; gap: 8px; }
        .message { max-width: 75%; padding: 8px 12px; border-radius: 8px; position: relative; font-size: 14px; word-break: break-word; }
        .message.received { background: #202c33; align-self: flex-start; border-top-left-radius: 0; }
        .message.sent { background: #005c4b; align-self: flex-end; border-top-right-radius: 0; }
        .message .time { font-size: 10px; color: #8696a0; float: right; margin-left: 8px; margin-top: 4px; line-height: 15px; }
        .revoked-tag { font-style: italic; color: #f15c6d; font-size: 12px; display: block; margin-bottom: 4px; }
        .delete-msg-btn { background: none; border: none; color: #8696a0; font-size: 10px; cursor: pointer; margin-left: 5px; }
        .delete-msg-btn:hover { color: #f15c6d; }

        /* Footer Input */
        .chat-footer { background: #202c33; padding: 10px 16px; display: flex; align-items: center; gap: 10px; }
        .chat-footer input { flex: 1; background: #2a3942; border: none; padding: 10px 14px; border-radius: 8px; color: #fff; outline: none; font-size: 14px; }
        .chat-footer button { background: #00a884; border: none; color: #fff; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .chat-footer button:hover { background: #008f72; }

        /* Modal GB Mods */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 100; }
        .modal-content { background: #111b21; padding: 24px; border-radius: 12px; width: 90%; max-width: 400px; border: 1px solid #2f3b43; }
        .modal-content h2 { color: #00a884; margin-bottom: 16px; font-size: 18px; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; font-size: 13px; color: #8696a0; margin-bottom: 6px; }
        .form-group input, .form-group select { width: 100%; background: #2a3942; border: 1px solid #374248; padding: 8px; border-radius: 6px; color: #fff; font-size: 14px; }
        .checkbox-group { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; font-size: 14px; cursor: pointer; }
        .modal-buttons { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
        .modal-buttons button { padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; }
        .btn-cancel { background: #222d34; color: #8696a0; }
        .btn-save { background: #00a884; color: #fff; }
    </style>
</head>
<body>

    <div class="container">
        <div class="header">
            <div class="header-left">
                <div class="avatar">GB</div>
                <div class="status-info">
                    <h3>WhatsApp GB Custom</h3>
                    <p id="status-text">Online (Modo Fantasma Ativo)</p>
                </div>
            </div>
            <button class="mods-btn" onclick="openMods()">⚙️ GB Mods</button>
        </div>

        <div class="chat-body" id="chat-body">
            <!-- As mensagens entram aqui dinamicamente -->
        </div>

        <div class="chat-footer">
            <input type="text" id="message-input" placeholder="Digite uma mensagem..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Enviar</button>
        </div>
    </div>

    <!-- Modal GB Mods -->
    <div class="modal" id="mods-modal">
        <div class="modal-content">
            <h2>⚙️ Configurações Avançadas GB</h2>
            
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

            <hr style="border: 0; border-top: 1px solid #2f3b43; margin: 15px 0;">

            <label class="checkbox-group">
                <input type="checkbox" id="anti-revoke"> 🛡️ Anti-Revogação (Impedir apagar mensagens)
            </label>
            <label class="checkbox-group">
                <input type="checkbox" id="freeze-last-seen"> ❄️ Congelar Visto por Último (Modo Fantasma)
            </label>
            <label class="checkbox-group">
                <input type="checkbox" id="anti-blue-tick"> 👀 Ocultar Confirmação de Leitura
            </label>
            <label class="checkbox-group">
                <input type="checkbox" id="ghost-mode"> 👻 Ocultar "Digitando..."
            </label>

            <div class="modal-buttons">
                <button class="btn-cancel" onclick="closeMods()">Cancelar</button>
                <button class="btn-save" onclick="saveMods()">Salvar Configurações</button>
            </div>
        </div>
    </div>

    <script>
        function loadMessages() {
            fetch('/get_messages')
                .then(res => res.json())
                .then(data => {
                    const chatBody = document.getElementById('chat-body');
                    chatBody.innerHTML = '';
                    data.messages.forEach(msg => {
                        let div = document.createElement('div');
                        div.className = `message ${msg.is_me ? 'sent' : 'received'}`;
                        
                        let content = '';
                        if (msg.revoked) {
                            content += `<span class="revoked-tag">🚫 [Esta mensagem foi apagada pelo contato]</span>`;
                        }
                        content += `<span>${msg.text}</span>`;
                        content += `<span class="time">${msg.time}</span>`;
                        
                        if (!msg.is_me) {
                            content += `<button class="delete-msg-btn" onclick="revokeMessage(${msg.id})" title="Simular apagar mensagem">[Apagar]</button>`;
                        }

                        div.innerHTML = content;
                        chatBody.appendChild(div);
                    });
                    chatBody.scrollTop = chatBody.scrollHeight;
                });
        }

        function sendMessage() {
            const input = document.getElementById('message-input');
            const text = input.value.trim();
            if (!text) return;

            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            }).then(() => {
                input.value = '';
                loadMessages();
            });
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') sendMessage();
        }

        function revokeMessage(id) {
            fetch('/revoke_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id })
            }).then(() => loadMessages());
        }

        function openMods() {
            fetch('/get_settings')
                .then(res => res.json())
                .then(settings => {
                    document.getElementById('api-key').value = settings.openai_api_key;
                    document.getElementById('ai-status').value = settings.ai_enabled.toString();
                    document.getElementById('anti-revoke').checked = settings.anti_revoke;
                    document.getElementById('freeze-last-seen').checked = settings.freeze_last_seen;
                    document.getElementById('anti-blue-tick').checked = settings.anti_blue_tick;
                    document.getElementById('ghost-mode').checked = settings.ghost_mode;
                    document.getElementById('mods-modal').style.display = 'flex';
                });
        }

        function closeMods() {
            document.getElementById('mods-modal').style.display = 'none';
        }

        function saveMods() {
            const settings = {
                openai_api_key: document.getElementById('api-key').value,
                ai_enabled: document.getElementById('ai-status').value === 'true',
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
                alert('Configurações GB salvas com sucesso!');
            });
        }

        setInterval(loadMessages, 3000);
        loadMessages();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
  return render_template_string(HTML_TEMPLATE)


@app.route("/get_messages", methods=["GET"])
def get_messages():
  return jsonify({"messages": mensagens})


@app.route("/send_message", methods=["POST"])
def send_message():
  data = request.json
  text = data.get("text", "")
  now = datetime.now().strftime("%H:%M")

  # Adiciona mensagem enviada por você
  msg_id = len(mensagens) + 1
  mensagens.append(
      {"id": msg_id, "sender": "Você", "text": text, "time": now, "is_me": True, "revoked": False}
  )

  # Se a IA estiver ativada, gera resposta inteligente (ou resposta manual limpa se desativada)
  if gb_settings["ai_enabled"] and gb_settings["openai_api_key"]:
    # Exemplo de integração OpenAI simplificada ou simulada inteligente
    resp_text = (
        f"🤖 [IA Ativa] Resposta inteligente baseada na sua mensagem: '{text}'"
    )
  else:
    # Modo manual puro: não envia resposta automática incômoda, apenas aguarda interações reais
    return jsonify({"status": "success"})

  import time

  time.sleep(1)
  resp_id = len(mensagens) + 1
  mensagens.append({
      "id": resp_id,
      "sender": "Assistente IA",
      "text": resp_text,
      "time": datetime.now().strftime("%H:%M"),
      "is_me": False,
      "revoked": False,
  })

  return jsonify({"status": "success"})


@app.route("/revoke_message", methods=["POST"])
def revoke_message():
  data = request.json
  msg_id = data.get("id")
  for m in mensagens:
    if m["id"] == msg_id:
      if gb_settings["anti_revoke"]:
        # Se o anti-revoke estiver ligado, marca como revogada mas mantém o texto visível!
        m["revoked"] = True
      else:
        m["text"] = "Esta mensagem foi apagada."
  return jsonify({"status": "success"})


@app.route("/get_settings", methods=["GET"])
def get_settings():
  return jsonify(gb_settings)


@app.route("/save_settings", methods=["POST"])
def save_settings():
  data = request.json
  gb_settings["openai_api_key"] = data.get("openai_api_key", "")
  gb_settings["ai_enabled"] = data.get("ai_enabled", False)
  gb_settings["anti_revoke"] = data.get("anti_revoke", True)
  gb_settings["freeze_last_seen"] = data.get("freeze_last_seen", True)
  gb_settings["anti_blue_tick"] = data.get("anti_blue_tick", True)
  gb_settings["ghost_mode"] = data.get("ghost_mode", True)
  return jsonify({"status": "success"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
