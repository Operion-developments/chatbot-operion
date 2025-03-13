from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import re
import asyncio
import random
import requests
import json
from datetime import datetime
import logging
from utils import get_saudacao, save_users_data, load_data
from orcamento import iniciar_orcamento, processar_orcamento

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OPERION_DATA = load_data("operion_data.json")
USERS_DATA = load_data("users.json", default={})
INTERACTIONS_DATA = load_data("interactions.json")
GEMINI_API_KEY = "AIzaSyC3K0A3tQK5WXX-2P13Z5rqnxog3bWbCaM"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    user_data["assunto"] = None
    user_data["awaiting_name"] = True
    user_data["last_message_time"] = datetime.now().timestamp()
    user_data.setdefault("orçamento", {})
    user_data.setdefault("historico", [])
    user_data.setdefault("nomes_vistos", set())
    user_data.setdefault("pending_messages", [])
    user_data.setdefault("current_user", None)
    user_data.setdefault("servicos_mencionados", [])
    user_data.setdefault("perguntas_count", 0)
    user_data.setdefault("respostas_orcamento", {})

    if chat_id in USERS_DATA and "nome" in USERS_DATA[chat_id]:
        nome = USERS_DATA[chat_id]["nome"]
        user_data["current_user"] = nome
        user_data["nomes_vistos"].add(nome)
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(f"{get_saudacao()}, {nome}! Tudo bem? Sou o Opi, da Operion. Como posso te ajudar hoje?\n\nA propósito, a qualquer momento você pode pedir pra falar com um especialista, tá?")
        user_data["awaiting_name"] = False
    else:
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(f"{get_saudacao()}! Tudo bem? Eu sou o Opi, da Operion. Qual é o seu nome?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    user_data.setdefault("orçamento", {})
    user_data.setdefault("historico", [])
    user_data.setdefault("nomes_vistos", set())
    user_data.setdefault("pending_messages", [])
    user_data.setdefault("current_user", None)
    user_data.setdefault("servicos_mencionados", [])
    user_data.setdefault("perguntas_count", 0)
    user_data.setdefault("respostas_orcamento", {})
    user_data["last_message_time"] = datetime.now().timestamp()

    mensagem = update.message.text
    logger.info(f"Received message: {mensagem}")

    user_data["pending_messages"].append({"text": mensagem, "timestamp": datetime.now().timestamp()})
    await asyncio.sleep(5)
    logger.info(f"Processing messages after 5 seconds. Pending messages: {user_data['pending_messages']}")

    mensagens = [msg["text"] for msg in user_data["pending_messages"]]
    user_data["pending_messages"] = []

    if not mensagens:
        logger.info("No messages to process.")
        return

    if chat_id not in USERS_DATA:
        USERS_DATA[chat_id] = {"nomes": []}

    nome = user_data["current_user"] if user_data["current_user"] else USERS_DATA[chat_id].get("nome", "você")
    nomes_vistos = user_data["nomes_vistos"]

    # Detectar troca de usuário
    for msg in mensagens:
        msg_lower = msg.lower()  # Definir msg_lower aqui
        nome_match = re.search(r"(?:me\s+chamo\s+|sou\s+[oa]?\s+)(\w+)", msg_lower, re.IGNORECASE)
        if nome_match:
            novo_nome = nome_match.group(1).capitalize()
            logger.info(f"Detected new name: {novo_nome}")
            if novo_nome not in nomes_vistos:
                nomes_vistos.add(novo_nome)
                if chat_id in USERS_DATA and "nomes" in USERS_DATA[chat_id]:
                    if novo_nome not in USERS_DATA[chat_id]["nomes"]:
                        USERS_DATA[chat_id]["nomes"].append(novo_nome)
                else:
                    USERS_DATA[chat_id]["nomes"] = [novo_nome]
                save_users_data(USERS_DATA)
            if novo_nome != nome:
                user_data["current_user"] = novo_nome
                if not user_data.get("awaiting_name"):
                    await update.message.reply_text(f"Olá, {novo_nome}! Notei que o {nome} não está por aqui agora. Como posso te ajudar hoje?")
                else:
                    await update.message.reply_text(f"Prazer em conhecer você, {novo_nome}! Como posso te ajudar hoje?\n\nA qualquer momento você pode pedir pra falar com um especialista, tá?")
                user_data["awaiting_name"] = False
            return

    # Adicionar ao histórico
    for msg in mensagens:
        user_data["historico"].append({"usuario": nome, "mensagem": msg})
    if len(user_data["historico"]) > 5:
        user_data["historico"] = user_data["historico"][-5:]

    # Detectar serviços mencionados
    servicos_detectados = set()
    for msg in mensagens:
        msg_lower = msg.lower()  # Definir msg_lower para cada mensagem no loop
        for solucao in OPERION_DATA["solucoes"]:
            if (solucao["slug"] in msg_lower or 
                solucao["title"].lower() in msg_lower or 
                "chatbot" in msg_lower and solucao["slug"] == "assistente-virtual" or
                "site" in msg_lower and solucao["slug"] in ["criacao-de-sites", "sites-prontos", "manutencao"] or
                "layout" in msg_lower and solucao["slug"] == "layouts" or
                "hospedagem" in msg_lower and solucao["slug"] == "hospedagem"):
                servicos_detectados.add(solucao["slug"])
    if servicos_detectados:
        user_data["servicos_mencionados"].extend(list(servicos_detectados))
        user_data["servicos_mencionados"] = list(set(user_data["servicos_mencionados"]))

    # Fluxo de orçamento
    if any(keyword in msg.lower() for msg in mensagens for keyword in ["orçamento", "quanto custa", "valores", "cotação", "preço"]):
        if user_data["servicos_mencionados"]:
            if len(user_data["servicos_mencionados"]) == 1:
                user_data["orçamento"]["serviço"] = user_data["servicos_mencionados"][0]
                await iniciar_orcamento(update, context, USERS_DATA)
            else:
                await update.message.reply_text(f"Você mencionou {', '.join(user_data['servicos_mencionados'])}. Quer um orçamento combinado pra esses serviços? Me conta o ramo do seu negócio pra eu começar!")
            return
        else:
            await update.message.reply_text(f"Beleza! Você quer um orçamento, né? Pode me dizer pra qual serviço? Tipo criação de site, chatbot, hospedagem...")
            return

    if user_data["orçamento"].get("step"):
        await processar_orcamento(update, context, USERS_DATA)
        return

    # Gemini com lógica de perguntas limitada
    historico_str = "\n".join([f"{h['usuario']}: {h['mensagem']}" for h in user_data["historico"]])
    respostas = []
    for msg in mensagens:
        msg_lower = msg.lower()  # Definir msg_lower aqui também
        if "especialista" in msg_lower:
            respostas.append("Claro, vou chamar um especialista pra te ajudar. Um minutinho!")
            continue
        if "tchau" in msg_lower or "obrigado" in msg_lower or "até mais" in msg_lower:
            respostas.append(f"Até mais, {nome}! Qualquer coisa, é só me chamar!")
            continue

        # Verificar se é resposta ao orçamento
        if user_data["perguntas_count"] > 0 and user_data["servicos_mencionados"]:
            servico_atual = user_data["servicos_mencionados"][0]
            user_data["respostas_orcamento"][servico_atual] = user_data["respostas_orcamento"].get(servico_atual, {})
            user_data["respostas_orcamento"][servico_atual][f"resposta_{user_data['perguntas_count']}"] = msg

        prompt = f"""
        Você é Opi, assistente virtual da Operion. Responda à mensagem "{msg}" de forma natural, fluida e humanizada, como um atendente experiente, seguindo as diretrizes abaixo. Use o contexto do histórico e os serviços mencionados para avançar a conversa.

        **Serviços da Operion:**
        {json.dumps(OPERION_DATA["solucoes"], ensure_ascii=False)}

        **Exemplos de Interações (inspiração, adapte ao contexto):**
        {json.dumps(INTERACTIONS_DATA, ensure_ascii=False)}

        **Histórico da conversa:**
        {historico_str}

        **Respostas do usuário para o orçamento:**
        {json.dumps(user_data["respostas_orcamento"], ensure_ascii=False)}

        **Regras:**
        - Use tom amigável e fluido, como um humano (ex.: "Ahh legal!", "Entendi!").
        - Não repita o nome do usuário nem saudações ("Tudo bem?") após o início da conversa, exceto no resumo final ou ao mudar de assunto.
        - Faça no máximo 3 mensagens de perguntas por serviço (controle via perguntas_count).
        - Após 3 perguntas ou se o usuário responder tudo, resuma as respostas e sugira uma reunião com especialista.
        - Não resuma o que o usuário disse a cada resposta; só no final, antes da reunião ou proposta.
        - Se o usuário mencionar um serviço claro (ex.: "site catálogo"), inicie perguntas específicas sem perguntar "qual serviço?".
        - Para perguntas técnicas (ex.: "Qual plataforma?"), explique brevemente (ex.: "Domínio é o endereço do site, como www.exemplo.com") e, se o usuário não souber, sugira uma reunião com especialista.
        - Se detectar múltiplos serviços, sugira um orçamento combinado no resumo final.
        - Se o usuário negar a reunião, ofereça falar com especialista no chat ou enviar proposta em 2h por e-mail ou chat.

        **Diretrizes de Orçamento:**
        - **Criação de Sites:** Perguntar: 1) Ramo de atuação; 2) Redes sociais e @; 3) Tipo de site (explicar: "Landing page é uma página única pra campanhas, e-commerce é loja online, etc.") + se tem domínio/hospedagem (explicar termos).
        - **Chatbots:** Perguntar: 1) Ramo de atuação; 2) Funcionalidade (explicar opções); 3) Canais (explicar IA vs. básico).
        - **Hospedagem:** Perguntar: 1) Ramo; 2) Já tem hospedagem/domínio? (explicar); 3) Necessidades (tráfego, e-mails).
        - **Layouts:** Perguntar: 1) Ramo; 2) Preferências de design; 3) Já tem site pra reformular?
        - **Sites Prontos:** Perguntar: 1) Ramo; 2) Personalização desejada; 3) Prazo.
        - **Manutenção:** Perguntar: 1) Ramo; 2) Problemas atuais do site; 3) Frequência desejada.

        **Contexto:**
        - Nome do usuário: {nome}
        - Assunto anterior: {user_data.get("assunto", "nenhum")}
        - Serviços mencionados: {', '.join(user_data["servicos_mencionados"]) if user_data["servicos_mencionados"] else "nenhum"}
        - Perguntas feitas: {user_data["perguntas_count"]}
        """
        logger.info(f"Sending prompt to Gemini: {prompt[:100]}...")
        response = requests.post(GEMINI_API_URL + "?key=" + GEMINI_API_KEY, headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": prompt}]}]})
        if response.status_code == 200:
            data = response.json()
            try:
                resposta = data["candidates"][0]["content"]["parts"][0]["text"]
                respostas.append(resposta)
                if "pergunta" in resposta.lower() or "?" in resposta:
                    user_data["perguntas_count"] += 1
                if user_data["perguntas_count"] >= 3 and user_data["servicos_mencionados"]:
                    respostas.append(await gerar_resumo_e_reuniao(user_data, nome))
                logger.info(f"Received response from Gemini: {resposta}")
            except KeyError as e:
                logger.error(f"Error parsing Gemini response: {str(e)}. Response: {json.dumps(data)}")
                respostas.append("Ops, algo deu errado ao processar sua mensagem. Pode tentar de novo?")
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            respostas.append(f"Ops, algo deu errado com a API: {response.status_code}. Tenta de novo?")

    for resposta in respostas:
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(resposta)

    user_data["assunto"] = "; ".join(mensagens)

async def gerar_resumo_e_reuniao(user_data, nome):
    servico = user_data["servicos_mencionados"][0] if user_data["servicos_mencionados"] else "desconhecido"
    respostas = user_data["respostas_orcamento"].get(servico, {})
    resumo = f"Beleza, {nome}! Pelo que entendi, você quer um {servico.replace('-', ' ')} "
    if servico == "criacao-de-sites" and respostas:
        resumo += f"pro seu negócio ({respostas.get('resposta_1', 'ramo não especificado')}), com {respostas.get('resposta_2', 'detalhes não especificados')}. "
    elif servico == "assistente-virtual":
        resumo += f"pra {respostas.get('resposta_2', 'funcionalidade não especificada')}, no seu negócio ({respostas.get('resposta_1', 'ramo não especificado')}). "
    if len(user_data["servicos_mencionados"]) > 1:
        resumo += f"E você também mencionou {', '.join(user_data['servicos_mencionados'][1:])}. Podemos incluir tudo num orçamento combinado! "
    resumo += "Obrigado por compartilhar essas infos, assim consigo entender melhor o que você precisa. Pra montar uma proposta personalizada e alinhar os detalhes, o ideal é marcarmos uma reunião rápida com um especialista via Google Meet. Qual dia e horário você tem disponível?"
    return resumo

async def check_inactivity(context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.now().timestamp()
    for chat_id, user_data in list(context.bot_data.items()):
        if "last_message_time" not in user_data:
            continue
        last_time = user_data["last_message_time"]
        if current_time - last_time >= 600:
            nome = user_data.get("current_user", "você")
            await context.bot.send_message(chat_id=chat_id, text=f"Oi, {nome}! Estou à disposição se você tiver qualquer dúvida, tá?")
            user_data["last_message_time"] = current_time