from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import re
import asyncio
import random
import requests
import json
from utils import get_saudacao, save_users_data, load_data
from orcamento import iniciar_orcamento, processar_orcamento

OPERION_DATA = load_data("operion_data.json")
USERS_DATA = load_data("users.json", default={})
GEMINI_API_KEY = "AIzaSyC3K0A3tQK5WXX-2P13Z5rqnxog3bWbCaM"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    user_data["assunto"] = None
    user_data["awaiting_name"] = True
    user_data.setdefault("orçamento", {})
    user_data.setdefault("historico", [])
    user_data.setdefault("nomes_vistos", set())

    if chat_id in USERS_DATA and "nome" in USERS_DATA[chat_id]:
        nome = USERS_DATA[chat_id]["nome"]
        user_data["nomes_vistos"].add(nome)
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(f"{get_saudacao()}, {nome}! Tudo bem? Como posso te ajudar hoje?\n\nA propósito, a qualquer momento você pode pedir pra falar com um especialista, tá?")
        user_data["awaiting_name"] = False
    else:
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(f"{get_saudacao()}! Tudo bem? Eu sou o Opi, da Operion. Qual é o seu nome?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text
    mensagem_lower = mensagem.lower()
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    user_data.setdefault("orçamento", {})
    user_data.setdefault("historico", [])
    user_data.setdefault("nomes_vistos", set())

    if chat_id not in USERS_DATA:
        USERS_DATA[chat_id] = {}

    nome = USERS_DATA[chat_id].get("nome", "você")
    nomes_vistos = user_data["nomes_vistos"]

    # Capturar nome inicial ou troca de usuário
    if user_data.get("awaiting_name") or "sou o" in mensagem_lower or "sou a" in mensagem_lower:
        nome_match = re.search(r"(?:me\s+chamo\s+|sou\s+[oa]?\s+)(\w+)", mensagem_lower, re.IGNORECASE)
        if nome_match:
            novo_nome = nome_match.group(1).capitalize()
            nomes_vistos.add(novo_nome)
            if novo_nome != nome:
                USERS_DATA[chat_id]["nome"] = novo_nome
                save_users_data(USERS_DATA)
                if not user_data.get("awaiting_name"):  # Troca de usuário
                    await asyncio.sleep(random.uniform(5, 15))
                    await update.message.chat.send_action(ChatAction.TYPING)
                    await asyncio.sleep(1)
                    await update.message.reply_text(f"Olá, {novo_nome}! Notei que o {nome} não está por aqui agora. Como posso te ajudar hoje?")
                else:  # Primeiro nome
                    await asyncio.sleep(random.uniform(5, 15))
                    await update.message.chat.send_action(ChatAction.TYPING)
                    await asyncio.sleep(1)
                    await update.message.reply_text(f"Prazer em conhecer você, {novo_nome}! Como posso te ajudar hoje?\n\nA propósito, a qualquer momento você pode pedir pra falar com um especialista, tá?")
                user_data["awaiting_name"] = False
            return
        elif user_data.get("awaiting_name"):
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Desculpe, não peguei seu nome direito. Pode me dizer como você se chama?")
            return

    # Abordagem descontraída se houver mais de um nome
    if len(nomes_vistos) > 1 and random.random() < 0.3:  # 30% de chance
        nomes_lista = list(nomes_vistos)
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(f"Olá! Com quem estou falando hoje, com o {nomes_lista[0]} ou a {nomes_lista[1]}? Kkk")
        return

    # Adicionar mensagem ao histórico (limite de 5 últimas mensagens)
    user_data["historico"].append({"usuario": nome, "mensagem": mensagem})
    if len(user_data["historico"]) > 5:
        user_data["historico"] = user_data["historico"][-5:]

    # Fluxo de orçamento com contexto
    if ("orçamento" in mensagem_lower or "quanto custa" in mensagem_lower or "valores" in mensagem_lower or "cotação" in mensagem_lower) and not user_data["orçamento"].get("step"):
        servico_mencionado = None
        for solucao in OPERION_DATA["solucoes"]:
            if solucao["slug"] in mensagem_lower or solucao["title"].lower() in mensagem_lower:
                servico_mencionado = solucao["slug"]
                break
        if not servico_mencionado:
            for h in user_data["historico"][:-1]:  # Verifica histórico exceto a mensagem atual
                for solucao in OPERION_DATA["solucoes"]:
                    if solucao["slug"] in h["mensagem"].lower() or solucao["title"].lower() in h["mensagem"].lower():
                        servico_mencionado = solucao["slug"]
                        break
                if servico_mencionado:
                    break

        if servico_mencionado:
            user_data["orçamento"]["serviço"] = servico_mencionado
            await iniciar_orcamento(update, context, USERS_DATA)
            return
        else:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Beleza, {nome}! Você quer um orçamento, né? Pode me dizer pra qual serviço? Tipo criação de site, chatbot, hospedagem...")
            return

    if user_data["orçamento"].get("step"):
        await processar_orcamento(update, context, USERS_DATA)
        return

    # Gemini com autonomia e contexto
    historico_str = "\n".join([f"{h['usuario']}: {h['mensagem']}" for h in user_data["historico"]])
    prompt = f"""
    Você é Opi, assistente da Operion. Converse com {nome} de forma profissional, amigável e fluida, como um atendente humano. Responda à mensagem "{mensagem}" de forma natural e objetiva, considerando o contexto da conversa. Aqui estão nossos serviços:
    {json.dumps(OPERION_DATA["solucoes"], ensure_ascii=False)}

    **Histórico da conversa:**
    {historico_str}

    **Regras:**
    - Use um tom natural e variado (ex.: "Bacana!", "Perfeito!", "Show!", "Beleza!", "Tranquilo!") sem repetir sempre as mesmas expressões como "Entendi" ou "Que legal".
    - Use o nome do usuário apenas na saudação inicial ou quando mudar de assunto, não em todas as respostas.
    - Seja objetivo: respostas curtas e diretas, exceto para explicações detalhadas (ex.: o que é domínio, como funciona um chatbot).
    - Se a mensagem for sobre orçamento, cotação ou valores e o serviço já estiver claro no histórico ou na mensagem (ex.: "site catálogo"), avance direto (ex.: "Tranquilo! Vamos precisar de algumas informações pra calcular o valor. Qual o ramo do seu negócio?").
    - Se o usuário pedir um especialista, responda: "Claro, vou chamar um especialista pra te ajudar. Um minutinho!"
    - Para despedidas (ex.: "tchau", "até mais"), responda: "Até mais, {nome}! Qualquer coisa, é só me chamar!"
    - Se não souber responder, diga: "Não sei ao certo, mas posso te ajudar com os serviços da Operion. O que você gostaria de saber?"
    - Sugira serviços da Operion se a mensagem for vaga (ex.: "Gostaria de um site" -> "Que tipo de site? Temos E-commerce, Institucional...").

    **Contexto:**
    - Nome atual do usuário: {nome}
    - Assunto anterior: {user_data.get("assunto", "nenhum")}
    
    Responda de forma adaptada à mensagem, mantendo o contexto do histórico.
    """
    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    response = requests.post(url, headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": prompt}]}]})
    
    if response.status_code != 200:
        await update.message.reply_text(f"Ops, {nome}, algo deu errado com a API: {response.status_code} - {response.text}")
        return
    
    data = response.json()
    try:
        resposta = data["candidates"][0]["content"]["parts"][0]["text"]
    except KeyError as e:
        await update.message.reply_text(f"Desculpe, {nome}, houve um problema com a resposta da API: {str(e)}. Aqui está o que recebi: {json.dumps(data)}")
        return
    
    await update.message.reply_text(resposta)
    user_data["assunto"] = mensagem