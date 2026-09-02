@app.get("/get_chats")
def get_chats():
    chats_list = []
    try:
        # Tenta buscar chats na Evolution API
        url = f"{EVOLUTION_URL}/chat/findChats/{INSTANCE_NAME}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            items = data if isinstance(data, list) else data.get("chats", [])
            for c in items:
                jid = c.get("id") or c.get("remoteJid", "")
                name = c.get("name") or c.get("pushName") or jid.split("@")[0]
                pic = c.get("profilePictureUrl") or c.get("pictureUrl", "")
                chats_list.append({
                    "id": jid,
                    "name": name,
                    "last_msg": "Conversa ativa",
                    "pic": pic,
                    "time": ""
                })
        
        # Se não achou chats, tenta buscar contatos da instância
        if not chats_list:
            url_contacts = f"{EVOLUTION_URL}/chat/findContacts/{INSTANCE_NAME}"
            res_c = requests.post(url_contacts, json={}, headers=headers, timeout=5)
            if res_c.status_code == 200:
                c_data = res_c.json()
                c_items = c_data if isinstance(c_data, list) else c_data.get("contacts", [])
                for c in c_items:
                    jid = c.get("id") or c.get("remoteJid", "")
                    name = c.get("name") or c.get("pushName") or jid.split("@")[0]
                    pic = c.get("profilePictureUrl", "")
                    chats_list.append({
                        "id": jid,
                        "name": name,
                        "last_msg": "Contato salvo",
                        "pic": pic,
                        "time": ""
                    })
    except Exception as e:
        print(f"Erro ao buscar chats/contatos: {e}")

    # Fallback para garantir que a interface nunca fique totalmente vazia e sem interação
    if not chats_list:
        chats_list.append({
            "id": "5543999999999@s.whatsapp.net",
            "name": "Exemplo Contato",
            "last_msg": "Olá via Evolution API",
            "pic": "",
            "time": "Agora"
        })

    return {
        "chats": chats_list,
        "theme": gb_settings["theme"]
    }
