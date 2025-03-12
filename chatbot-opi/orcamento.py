from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import asyncio
import random
from utils import save_users_data, load_data

async def iniciar_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE, users_data):
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    nome = users_data[chat_id]["nome"]
    serviço = user_data["orçamento"]["serviço"]

    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    await update.message.reply_text(f"Tranquilo, {nome}! Vamos montar um orçamento pra você. Qual é o ramo de atuação do seu negócio?")
    user_data["orçamento"]["step"] = "ramo"

async def processar_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE, users_data):
    mensagem = update.message.text
    mensagem_lower = mensagem.lower()
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    nome = users_data[chat_id]["nome"]
    serviço = user_data["orçamento"]["serviço"]
    orçamento = user_data["orçamento"]

    if serviço == "criacao-de-sites":
        if orçamento["step"] == "ramo":
            orçamento["ramo"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Show! Um negócio no ramo de {mensagem} parece bem interessante! Você tem redes sociais do seu negócio, como Instagram, LinkedIn ou Facebook?")
            orçamento["step"] = "redes"
        elif orçamento["step"] == "redes":
            if "sim" in mensagem_lower or "@" in mensagem:
                orçamento["redes"] = mensagem
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Perfeito! Pode compartilhar o @ das suas redes pra gente dar uma olhada?")
                orçamento["step"] = "redes_link"
            else:
                orçamento["redes"] = "não"
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Sem problemas! Você já possui ou possuiu um site pra sua empresa?")
                orçamento["step"] = "site_existente"
        elif orçamento["step"] == "redes_link":
            orçamento["redes_link"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Ahh, legal! Vou dar uma olhada no {mensagem} depois. Você já possui ou possuiu um site pra sua empresa?")
            orçamento["step"] = "site_existente"
        elif orçamento["step"] == "site_existente":
            orçamento["site_existente"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Beleza! Qual tipo de site você precisa? Pode ser:\n- Landing Page\n- E-commerce\n- Site Institucional\n- Site Catálogo")
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text("Caso queira, eu te explico como cada um funciona pra você escolher melhor!")
            orçamento["step"] = "tipo_site"
        elif orçamento["step"] == "tipo_site":
            if "explic" in mensagem_lower:
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Claro! Aqui vai uma explicação rápida:\n- **Landing Page**: Uma página simples pra campanhas ou captar contatos.\n- **E-commerce**: Uma loja online pra vender produtos.\n- **Site Institucional**: Pra apresentar sua empresa, com 'Sobre', 'Serviços', etc.\n- **Site Catálogo**: Pra mostrar produtos sem venda direta, tipo um portfólio.\nQual você acha que é o ideal pro seu caso?")
            else:
                orçamento["tipo_site"] = mensagem
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Ótimo, {mensagem} é uma boa escolha! Você já tem um domínio pro site? Tipo www.suaempresa.com.br? Se não souber o que é, eu te explico!")
                orçamento["step"] = "dominio"
        elif orçamento["step"] == "dominio":
            if "explic" in mensagem_lower:
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Sem problema! O domínio é o endereço do seu site na internet, tipo www.suaempresa.com.br. É como as pessoas te encontram online. Você já tem um registrado ou precisa de ajuda pra escolher um?")
            else:
                orçamento["dominio"] = mensagem
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Tranquilo! E sobre hospedagem, você já usa alguma pra e-mail ou site? Se não souber o que é hospedagem, posso te explicar!")
                orçamento["step"] = "hospedagem"
        elif orçamento["step"] == "hospedagem":
            if "explic" in mensagem_lower:
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Claro! Hospedagem é o serviço que mantém seu site no ar e funcionando na internet. É como um 'aluguel' de espaço online. Pode incluir e-mails personalizados também, tipo contato@suaempresa.com.br. Você já tem algo assim ou quer que a gente te ofereça um plano?")
            else:
                orçamento["hospedagem"] = mensagem
                await finalizar_orcamento(update, context, users_data)

    elif serviço == "assistente-virtual":
        if orçamento["step"] == "ramo":
            orçamento["ramo"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Bacana! Um negócio no ramo de {mensagem} tem muito potencial! Você tem redes sociais do seu negócio, como Instagram, LinkedIn ou Facebook?")
            orçamento["step"] = "redes"
        elif orçamento["step"] == "redes":
            if "sim" in mensagem_lower or "@" in mensagem:
                orçamento["redes"] = mensagem
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Ótimo! Pode compartilhar o @ das suas redes pra gente dar uma olhada?")
                orçamento["step"] = "redes_link"
            else:
                orçamento["redes"] = "não"
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Sem problemas! Você já possui ou possuiu um site pra sua empresa?")
                orçamento["step"] = "site_existente"
        elif orçamento["step"] == "redes_link":
            orçamento["redes_link"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Ahh, legal! Vou dar uma olhada no {mensagem} depois. Você já possui ou possuiu um site pra sua empresa?")
            orçamento["step"] = "site_existente"
        elif orçamento["step"] == "site_existente":
            orçamento["site_existente"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Beleza! Pra qual seria a funcionalidade do chatbot? Pode ser:\n- Atendimento ao cliente (WhatsApp/Telegram/Site)\n- Chatbot Oráculo (armazena informações da empresa)\n- Suporte técnico (WhatsApp/Telegram/Site)\n- Primeiro contato (Básico)\n- Chatbot Premium (tudo incluso)")
            orçamento["step"] = "funcionalidade_chatbot"
        elif orçamento["step"] == "funcionalidade_chatbot":
            if "atendimento" in mensagem_lower or "suporte" in mensagem_lower or "premium" in mensagem_lower:
                orçamento["funcionalidade_chatbot"] = mensagem
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Show! Pra quantos canais você precisa? Só WhatsApp, site, ou mais de um? Se quiser, explico como funciona um chatbot de atendimento com IA!")
                orçamento["step"] = "canais_chatbot"
            elif "básico" in mensagem_lower:
                orçamento["funcionalidade_chatbot"] = "básico"
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Tranquilo! O chatbot básico funciona como um filtro, direcionando o cliente pro canal certo, sem IA. Quer saber mais ou já podemos avançar?")
                orçamento["step"] = "confirmar_basico"
            elif "oráculo" in mensagem_lower or "oraculo" in mensagem_lower:
                orçamento["funcionalidade_chatbot"] = "oráculo"
                await finalizar_orcamento(update, context, users_data)
            else:
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Não peguei direito. Pode dizer qual funcionalidade você quer? Atendimento, Suporte, Oráculo, Básico ou Premium?")
        elif orçamento["step"] == "canais_chatbot":
            if "explic" in mensagem_lower:
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Claro! Um chatbot de atendimento com IA faz todo o processo de atendimento: responde perguntas, resolve dúvidas e até direciona o cliente, tudo automaticamente. Pra quantos canais você precisa? WhatsApp, site, ou mais?")
            else:
                orçamento["canais_chatbot"] = mensagem
                await finalizar_orcamento(update, context, users_data)
        elif orçamento["step"] == "confirmar_basico":
            if "sim" in mensagem_lower or "mais" in mensagem_lower:
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"O básico é simples: mostra opções como 'Agendar consulta' ou 'Pegar exame' e direciona o cliente pro canal certo. Sem IA, mas bem eficiente! Quer avançar?")
            else:
                await finalizar_orcamento(update, context, users_data)

    elif serviço == "hospedagem":
        if orçamento["step"] == "ramo":
            orçamento["ramo"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Perfeito! Você já usa alguma hospedagem pra site ou e-mail? Se não souber o que é, posso te explicar!")
            orçamento["step"] = "hospedagem_existente"
        elif orçamento["step"] == "hospedagem_existente":
            if "explic" in mensagem_lower:
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Sem problema! Hospedagem é o serviço que mantém seu site no ar e pode incluir e-mails personalizados, como contato@suaempresa.com.br. Você já tem algo assim ou quer um plano nosso?")
            else:
                orçamento["hospedagem_existente"] = mensagem
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Beleza! Quantos e-mails personalizados você acha que vai precisar? E o site, já tem um ou vai criar?")
                orçamento["step"] = "detalhes_hospedagem"
        elif orçamento["step"] == "detalhes_hospedagem":
            orçamento["detalhes_hospedagem"] = mensagem
            await finalizar_orcamento(update, context, users_data)

    elif serviço == "layouts-prontos" or serviço == "sites-prontos":
        if orçamento["step"] == "ramo":
            orçamento["ramo"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Show! Você tem redes sociais do seu negócio pra gente se inspirar no estilo? Instagram, LinkedIn, Facebook?")
            orçamento["step"] = "redes"
        elif orçamento["step"] == "redes":
            if "sim" in mensagem_lower or "@" in mensagem:
                orçamento["redes"] = mensagem
                await asyncio.sleep(random.uniform(5, 15))
                await update.message.chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(1)
                await update.message.reply_text(f"Ótimo! Pode mandar o @ pra gente dar uma olhada?")
                orçamento["step"] = "redes_link"
            else:
                orçamento["redes"] = "não"
                await finalizar_orcamento(update, context, users_data)
        elif orçamento["step"] == "redes_link":
            orçamento["redes_link"] = mensagem
            await finalizar_orcamento(update, context, users_data)

    elif serviço == "manutencao-de-site":
        if orçamento["step"] == "ramo":
            orçamento["ramo"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Tranquilo! Você já tem um site que precisa de manutenção? Pode mandar o link se tiver!")
            orçamento["step"] = "site_existente"
        elif orçamento["step"] == "site_existente":
            orçamento["site_existente"] = mensagem
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Beleza! Qual o tipo de manutenção você precisa? Atualizações, correções, backups...?")
            orçamento["step"] = "tipo_manutencao"
        elif orçamento["step"] == "tipo_manutencao":
            orçamento["tipo_manutencao"] = mensagem
            await finalizar_orcamento(update, context, users_data)

async def finalizar_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE, users_data):
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    nome = users_data[chat_id]["nome"]
    serviço = user_data["orçamento"]["serviço"]

    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    await update.message.reply_text(f"Muito obrigado por compartilhar tudo isso, {nome}! Com essas informações, dá pra entender bem o que você precisa e montar uma proposta personalizada.")
    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    if serviço == "assistente-virtual":
        await update.message.reply_text(f"Como é um chatbot, precisamos alinhar as funcionalidades direitinho. O ideal é marcarmos uma reunião via Google Meet com nosso especialista pra apresentar a proposta e entender ainda mais o que você espera. Qual dia e horário você tem disponível?")
    else:
        await update.message.reply_text(f"Agora, pra concluirmos o orçamento e te apresentar a proposta, o ideal é marcarmos uma reunião via Google Meet com nosso especialista. Ele vai te mostrar tudo e entender ainda mais sobre seu projeto. Qual dia e horário você tem disponível?")
    user_data["orçamento"]["step"] = "reuniao"

    # Processar resposta sobre reunião
    mensagem_lower = update.message.text.lower()
    if user_data["orçamento"]["step"] == "reuniao":
        if "não" in mensagem_lower or "nao" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Sem problemas! Você prefere falar com um especialista por aqui mesmo?")
            user_data["orçamento"]["step"] = "especialista"
        elif "sim" in mensagem_lower or "dia" in mensagem_lower or "horário" in mensagem_lower or "horario" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Perfeito! Pode mandar o dia e horário que funciona pra você!")
            user_data["orçamento"]["step"] = "agendar_reuniao"
        else:
            return  # Espera próxima mensagem

    # Processar resposta sobre especialista
    if user_data["orçamento"]["step"] == "especialista":
        if "não" in mensagem_lower or "nao" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Tudo bem! Dentro de até 2 horas, vamos te enviar a proposta. Você prefere receber por e-mail ou aqui pelo chat?")
            user_data["orçamento"]["step"] = "canal_proposta"
        elif "sim" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Ótimo! Vou chamar um especialista pra continuar com você aqui. Um minutinho!")
            user_data["orçamento"]["step"] = None
        else:
            return  # Espera próxima mensagem

    # Processar canal da proposta
    if user_data["orçamento"].get("step") == "canal_proposta":
        if "email" in mensagem_lower or "e-mail" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Beleza! Qual endereço de e-mail é melhor pra gente enviar a proposta?")
            user_data["orçamento"]["step"] = "email"
        elif "chat" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Por enquanto é isso, {nome}! Desde já agradecemos o seu contato e estamos muito felizes em ajudar seu projeto a virar realidade. Qualquer dúvida, é só me chamar, viu?")
            user_data["orçamento"]["step"] = None
        else:
            return  # Espera próxima mensagem

    # Processar e-mail
    if user_data["orçamento"].get("step") == "email":
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(f"Perfeito! Vamos enviar a proposta pro {mensagem} em até 2 horas. Qualquer coisa, é só me chamar aqui!")
        user_data["orçamento"]["step"] = None

    # Processar agendamento da reunião
    if user_data["orçamento"].get("step") == "agendar_reuniao":
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(f"Combinado! Vamos marcar a reunião para {mensagem}. Nosso especialista vai te contatar pra confirmar. Qualquer coisa, é só me chamar!")
        user_data["orçamento"]["step"] = None