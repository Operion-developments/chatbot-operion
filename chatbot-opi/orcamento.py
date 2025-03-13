from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import asyncio
import random
from utils import save_users_data, load_data

async def iniciar_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE, users_data):
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    nome = users_data[chat_id].get("nome", "você")
    serviço = user_data["orçamento"]["serviço"]

    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    await update.message.reply_text(f"Vamos montar um orçamento pra você. Qual é o ramo de atuação do seu negócio?")
    user_data["orçamento"]["step"] = "ramo"

async def processar_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE, users_data):
    mensagem = update.message.text
    mensagem_lower = mensagem.lower()
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    nome = users_data[chat_id].get("nome", "você")
    serviço = user_data["orçamento"]["serviço"]
    orçamento = user_data["orçamento"]

    if serviço == "manutencao-de-site":
        if orçamento["step"] == "ramo":
            orçamento["ramo"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            resposta = "Você já tem um site que precisa de manutenção? Pode mandar o link se tiver!"
            if random.random() < 0.2:  # 20% de chance de palavra descontraída
                resposta = "Tranquilo! " + resposta
            await update.message.reply_text(resposta)
            orçamento["step"] = "site_existente"
        elif orçamento["step"] == "site_existente":
            orçamento["site_existente"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            resposta = "Qual o tipo de manutenção você precisa? Atualizações, correções, backups...?"
            if random.random() < 0.2:
                resposta = "Beleza! " + resposta
            await update.message.reply_text(resposta)
            orçamento["step"] = "tipo_manutencao"
        elif orçamento["step"] == "tipo_manutencao":
            orçamento["tipo_manutencao"] = mensagem
            await finalizar_orcamento(update, context, users_data)

async def finalizar_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE, users_data):
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    nome = users_data[chat_id].get("nome", "você")

    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    await update.message.reply_text(f"Muito obrigado por compartilhar tudo isso, {nome}! Com essas informações, dá pra entender bem o que você precisa e montar uma proposta personalizada.")
    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    await update.message.reply_text(f"Agora, pra concluirmos o orçamento e te apresentar a proposta, o ideal é marcarmos uma reunião via Google Meet com nosso especialista. Qual dia e horário você tem disponível?")
    user_data["orçamento"]["step"] = "reuniao"