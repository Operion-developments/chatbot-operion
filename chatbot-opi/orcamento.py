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

    user_data["orçamento"]["step"] = "primarias"
    user_data["respostas_orcamento"][serviço] = {}
    user_data["perguntas_count"] = 0

    # Verifica o histórico para preencher informações já fornecidas
    historico = user_data.get("historico", [])
    for entry in historico:
        msg_lower = entry["mensagem"].lower()
        if "marketing" in msg_lower or "empresa" in msg_lower:
            user_data["respostas_orcamento"][serviço]["ramo"] = entry["mensagem"]

    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    mensagem_primarias = (
        f"Ahh legal, {nome}! Vamos montar um orçamento pro seu {serviço.replace('-', ' ')}. "
        "Pra começar, me ajuda com algumas infos:\n"
        "1. Qual o nome da sua empresa?\n"
        "2. Qual o ramo de atuação dela? (Se já me contou, só confirma!)\n"
        "3. Tem redes sociais como Instagram ou Facebook? Se sim, quais os @?\n"
        "4. Já tem um domínio, tipo www.suaempresa.com.br?\n"
        "5. E hospedagem, já possui ou precisa que a gente inclua?"
    )
    await update.message.reply_text(mensagem_primarias)
    user_data["perguntas_count"] = 1  # Conta como 1 mensagem de perguntas

async def processar_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE, users_data):
    mensagem = update.message.text
    mensagem_lower = mensagem.lower()
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    nome = users_data[chat_id].get("nome", "você")
    serviço = user_data["orçamento"]["serviço"]
    orçamento = user_data["orçamento"]
    respostas = user_data["respostas_orcamento"][serviço]
    perguntas_count = user_data["perguntas_count"]

    # Processar respostas primárias
    if orçamento["step"] == "primarias":
        # Tenta extrair respostas da mensagem do usuário
        linhas = mensagem.split("\n")
        for linha in linhas:
            linha_lower = linha.lower()
            if "nome" in linha_lower or "empresa" in linha_lower:
                respostas["nome"] = linha.strip()
            elif "ramo" in linha_lower or "atuação" in linha_lower or "marketing" in linha_lower:
                respostas["ramo"] = linha.strip()
            elif "redes" in linha_lower or "@" in linha_lower or "instagram" in linha_lower or "facebook" in linha_lower:
                respostas["redes"] = linha.strip() if "não" not in linha_lower else "Nenhuma"
            elif "domínio" in linha_lower or "www" in linha_lower or ".com" in linha_lower:
                respostas["dominio"] = linha.strip() if "não" not in linha_lower else "Não possui"
            elif "hospedagem" in linha_lower:
                respostas["hospedagem"] = linha.strip() if "não" not in linha_lower else "Não possui"

        # Perguntas secundárias específicas por serviço
        if serviço == "assistente-virtual" and perguntas_count < 3:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(
                f"Show, {nome}! Agora sobre o chatbot:\n"
                "1. Qual a função principal dele? (Ex.: atendimento, suporte, organizar infos)\n"
                "2. Em quais canais quer usá-lo? (WhatsApp, Telegram, site, etc.)\n"
                "3. Tem alguma funcionalidade específica em mente? (Ex.: integração com CRM)\n"
                "4. Qual o volume de interações que você espera por mês?\n"
                "5. Já tem algum exemplo de chatbot que gosta?"
            )
            orçamento["step"] = "secundarias_chatbot"
            user_data["perguntas_count"] += 1
        elif serviço == "criacao-de-sites" and perguntas_count < 3:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(
                f"Show, {nome}! Agora sobre a criação do site:\n"
                "1. Que tipo de site você precisa? (Ex.: institucional, e-commerce, landing page, portfólio)\n"
                "2. Qual o estilo de design que você prefere? (Ex.: moderno, minimalista, colorido)\n"
                "3. Tem funcionalidades específicas em mente? (Ex.: loja virtual, blog, formulário de contato)\n"
                "4. Quantas páginas ou seções o site deve ter? (Ex.: 5 páginas, 10 produtos)\n"
                "5. Tem algum site como referência que você gosta?"
            )
            orçamento["step"] = "secundarias_criacao_de_sites"
            user_data["perguntas_count"] += 1
        elif serviço == "hospedagem" and perguntas_count < 3:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(
                f"Tranquilo, {nome}! Sobre a hospedagem:\n"
                "1. Quantos visitantes espera por mês?\n"
                "2. Precisa de e-mails profissionais? Quantos?\n"
                "3. Tem previsão de tráfego alto ou sazonal?\n"
                "4. Quer backups automáticos inclusos?\n"
                "5. Já usa alguma plataforma como WordPress?"
            )
            orçamento["step"] = "secundarias_hospedagem"
            user_data["perguntas_count"] += 1
        elif serviço == "sites-prontos" and perguntas_count < 3:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(
                f"Beleza, {nome}! Sobre o site pronto:\n"
                "1. Quer personalizar com sua marca (cores, logo)?\n"
                "2. Qual o prazo pra colocar no ar?\n"
                "3. Precisa de funcionalidades extras? (Ex.: blog, formulário)\n"
                "4. Qual o foco do site? (Ex.: vendas, divulgação)\n"
                "5. Tem um exemplo de site que gosta?"
            )
            orçamento["step"] = "secundarias_sites_prontos"
            user_data["perguntas_count"] += 1
        elif serviço == "layouts" and perguntas_count < 3:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(
                f"Show, {nome}! Sobre o layout:\n"
                "1. Qual o estilo de design? (Moderno, minimalista, etc.)\n"
                "2. É pra site, app ou ambos?\n"
                "3. Já tem um site/app pra aplicar? Se sim, qual o link?\n"
                "4. Tem algum exemplo de layout que curte?\n"
                "5. Precisa de animações ou interatividade?"
            )
            orçamento["step"] = "secundarias_layouts"
            user_data["perguntas_count"] += 1
        elif serviço == "manutencao" and perguntas_count < 3:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(
                f"Legal, {nome}! Sobre a manutenção:\n"
                "1. Que tipo de manutenção precisa? (Atualizações, bugs, backups)\n"
                "2. Qual a frequência? (Semanal, mensal, sob demanda)\n"
                "3. Qual o site ou sistema a ser mantido?\n"
                "4. Tem problemas específicos agora?\n"
                "5. Quer monitoramento de uptime?"
            )
            orçamento["step"] = "secundarias_manutencao"
            user_data["perguntas_count"] += 1
        else:
            await finalizar_orcamento(update, context, users_data)

    # Processar respostas secundárias
    elif orçamento["step"].startswith("secundarias_"):
        linhas = mensagem.split("\n")
        if serviço == "assistente-virtual" and orçamento["step"] == "secundarias_chatbot":
            for linha in linhas:
                linha_lower = linha.lower()
                if "função" in linha_lower or "atendimento" in linha_lower or "suporte" in linha_lower or "organizar" in linha_lower:
                    respostas["funcionalidade"] = linha.strip()
                elif "canais" in linha_lower or "whatsapp" in linha_lower or "telegram" in linha_lower or "site" in linha_lower:
                    respostas["canais"] = linha.strip()
                elif "funcionalidade" in linha_lower or "crm" in linha_lower or "específica" in linha_lower:
                    respostas["funcionalidade_extra"] = linha.strip()
                elif "volume" in linha_lower or "interações" in linha_lower or "mês" in linha_lower:
                    respostas["volume"] = linha.strip()
                elif "exemplo" in linha_lower or "gosta" in linha_lower:
                    respostas["exemplo"] = linha.strip()
            await finalizar_orcamento(update, context, users_data)
        elif serviço == "criacao-de-sites" and orçamento["step"] == "secundarias_criacao_de_sites":
            for linha in linhas:
                linha_lower = linha.lower()
                if "tipo" in linha_lower or "institucional" in linha_lower or "e-commerce" in linha_lower or "landing" in linha_lower or "portfólio" in linha_lower:
                    respostas["tipo_site"] = linha.strip()
                elif "estilo" in linha_lower or "design" in linha_lower or "moderno" in linha_lower or "minimalista" in linha_lower or "colorido" in linha_lower:
                    respostas["design"] = linha.strip()
                elif "funcionalidades" in linha_lower or "loja" in linha_lower or "blog" in linha_lower or "formulário" in linha_lower:
                    respostas["funcionalidades"] = linha.strip()
                elif "páginas" in linha_lower or "seções" in linha_lower or "produtos" in linha_lower:
                    respostas["quantidade_paginas"] = linha.strip()
                elif "referência" in linha_lower or "exemplo" in linha_lower or "gosta" in linha_lower:
                    respostas["exemplo"] = linha.strip()
            await finalizar_orcamento(update, context, users_data)
        elif serviço == "hospedagem" and orçamento["step"] == "secundarias_hospedagem":
            for linha in linhas:
                linha_lower = linha.lower()
                if "visitantes" in linha_lower or "mês" in linha_lower or "tráfego" in linha_lower:
                    respostas["trafego"] = linha.strip()
                elif "e-mails" in linha_lower or "profissionais" in linha_lower or "quantos" in linha_lower:
                    respostas["emails"] = linha.strip()
                elif "sazonal" in linha_lower or "alto" in linha_lower or "previsão" in linha_lower:
                    respostas["trafego_sazonal"] = linha.strip()
                elif "backups" in linha_lower or "automáticos" in linha_lower:
                    respostas["backups"] = linha.strip()
                elif "plataforma" in linha_lower or "wordpress" in linha_lower or "usa" in linha_lower:
                    respostas["plataforma"] = linha.strip()
            await finalizar_orcamento(update, context, users_data)
        elif serviço == "sites-prontos" and orçamento["step"] == "secundarias_sites_prontos":
            for linha in linhas:
                linha_lower = linha.lower()
                if "personalizar" in linha_lower or "marca" in linha_lower or "cores" in linha_lower or "logo" in linha_lower:
                    respostas["personalizacao"] = linha.strip()
                elif "prazo" in linha_lower or "ar" in linha_lower or "colocar" in linha_lower:
                    respostas["prazo"] = linha.strip()
                elif "funcionalidades" in linha_lower or "extras" in linha_lower or "blog" in linha_lower or "formulário" in linha_lower:
                    respostas["funcionalidades"] = linha.strip()
                elif "foco" in linha_lower or "vendas" in linha_lower or "divulgação" in linha_lower:
                    respostas["foco"] = linha.strip()
                elif "exemplo" in linha_lower or "gosta" in linha_lower or "site" in linha_lower:
                    respostas["exemplo"] = linha.strip()
            await finalizar_orcamento(update, context, users_data)
        elif serviço == "layouts" and orçamento["step"] == "secundarias_layouts":
            for linha in linhas:
                linha_lower = linha.lower()
                if "estilo" in linha_lower or "design" in linha_lower or "moderno" in linha_lower or "minimalista" in linha_lower:
                    respostas["design"] = linha.strip()
                elif "site" in linha_lower or "app" in linha_lower or "ambos" in linha_lower:
                    respostas["tipo"] = linha.strip()
                elif "link" in linha_lower or "aplicar" in linha_lower or "existente" in linha_lower:
                    respostas["site_existente"] = linha.strip()
                elif "exemplo" in linha_lower or "curte" in linha_lower:
                    respostas["exemplo"] = linha.strip()
                elif "animações" in linha_lower or "interatividade" in linha_lower:
                    respostas["interatividade"] = linha.strip()
            await finalizar_orcamento(update, context, users_data)
        elif serviço == "manutencao" and orçamento["step"] == "secundarias_manutencao":
            for linha in linhas:
                linha_lower = linha.lower()
                if "tipo" in linha_lower or "atualizações" in linha_lower or "bugs" in linha_lower or "backups" in linha_lower:
                    respostas["tipo_manutencao"] = linha.strip()
                elif "frequência" in linha_lower or "semanal" in linha_lower or "mensal" in linha_lower or "demanda" in linha_lower:
                    respostas["frequencia"] = linha.strip()
                elif "site" in linha_lower or "sistema" in linha_lower or "mantido" in linha_lower:
                    respostas["site_sistema"] = linha.strip()
                elif "problemas" in linha_lower or "específicos" in linha_lower or "agora" in linha_lower:
                    respostas["problemas"] = linha.strip()
                elif "monitoramento" in linha_lower or "uptime" in linha_lower:
                    respostas["monitoramento"] = linha.strip()
            await finalizar_orcamento(update, context, users_data)

    # Lógica de reunião e recusa
    elif orçamento["step"] == "reuniao":
        if "não" in mensagem_lower or "nao" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Sem problemas, {nome}! Você prefere falar com um especialista por aqui ou quer que eu envie a proposta em até 2 horas? Pode ser por e-mail ou aqui no chat, você escolhe!")
            orçamento["step"] = "opcao_recusa"
        else:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Perfeito, {nome}! Vou agendar a reunião pro dia e horário que você mencionou. Te envio o link do Google Meet em breve!")
            orçamento["step"] = None

    elif orçamento["step"] == "opcao_recusa":
        if "chat" in mensagem_lower or "aqui" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Beleza, {nome}! Um especialista vai te atender por aqui em breve. Enquanto isso, qualquer dúvida é só me chamar!")
            orçamento["step"] = None
        elif "e-mail" in mensagem_lower or "email" in mensagem_lower:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Tranquilo! Qual endereço de e-mail você prefere pra receber a proposta?")
            orçamento["step"] = "email"
        else:
            await asyncio.sleep(random.uniform(5, 15))
            await update.message.chat.send_action(ChatAction.TYPING)
            await asyncio.sleep(1)
            await update.message.reply_text(f"Desculpe, não entendi. Você quer falar com um especialista por aqui ou prefere receber a proposta por e-mail?")

    elif orçamento["step"] == "email":
        respostas["email"] = mensagem
        await asyncio.sleep(random.uniform(5, 15))
        await update.message.chat.send_action(ChatAction.TYPING)
        await asyncio.sleep(1)
        await update.message.reply_text(f"Show, {nome}! Vamos enviar a proposta pro {mensagem} em até 2 horas. Qualquer coisa, é só me chamar aqui!")
        orçamento["step"] = None

async def finalizar_orcamento(update: Update, context: ContextTypes.DEFAULT_TYPE, users_data):
    chat_id = str(update.message.chat_id)
    user_data = context.user_data
    nome = users_data[chat_id].get("nome", "você")
    serviço = user_data["orçamento"]["serviço"]
    respostas = user_data["respostas_orcamento"][serviço]

    resumo = f"Beleza, {nome}! Pelo que entendi, você precisa:\n"
    if serviço == "assistente-virtual":
        resumo += "- Chatbot\n"
        if "funcionalidade" in respostas:
            resumo += f"- Função: {respostas['funcionalidade']}\n"
        if "canais" in respostas:
            resumo += f"- Canais: {respostas['canais']}\n"
        if "funcionalidade_extra" in respostas:
            resumo += f"- Funcionalidade Extra: {respostas['funcionalidade_extra']}\n"
        if "volume" in respostas:
            resumo += f"- Volume Esperado: {respostas['volume']}\n"
        if "exemplo" in respostas:
            resumo += f"- Exemplo: {respostas['exemplo']}\n"
    elif serviço == "criacao-de-sites":
        resumo += "- Criação de Site\n"
        if "tipo_site" in respostas:
            resumo += f"- Tipo: {respostas['tipo_site']}\n"
        if "design" in respostas:
            resumo += f"- Estilo de Design: {respostas['design']}\n"
        if "funcionalidades" in respostas:
            resumo += f"- Funcionalidades: {respostas['funcionalidades']}\n"
        if "quantidade_paginas" in respostas:
            resumo += f"- Quantidade de Páginas/Seções: {respostas['quantidade_paginas']}\n"
        if "exemplo" in respostas:
            resumo += f"- Referência: {respostas['exemplo']}\n"
    elif serviço == "hospedagem":
        resumo += "- Hospedagem otimizada\n"
        if "trafego" in respostas:
            resumo += f"- Tráfego Estimado: {respostas['trafego']}\n"
        if "emails" in respostas:
            resumo += f"- E-mails: {respostas['emails']}\n"
        if "trafego_sazonal" in respostas:
            resumo += f"- Tráfego Sazonal: {respostas['trafego_sazonal']}\n"
        if "backups" in respostas:
            resumo += f"- Backups: {respostas['backups']}\n"
        if "plataforma" in respostas:
            resumo += f"- Plataforma: {respostas['plataforma']}\n"
    elif serviço == "sites-prontos":
        resumo += "- Site a pronta entrega\n"
        if "personalizacao" in respostas:
            resumo += f"- Personalização: {respostas['personalizacao']}\n"
        if "prazo" in respostas:
            resumo += f"- Prazo: {respostas['prazo']}\n"
        if "funcionalidades" in respostas:
            resumo += f"- Funcionalidades: {respostas['funcionalidades']}\n"
        if "foco" in respostas:
            resumo += f"- Foco: {respostas['foco']}\n"
        if "exemplo" in respostas:
            resumo += f"- Exemplo: {respostas['exemplo']}\n"
    elif serviço == "layouts":
        resumo += "- Layout para site ou app\n"
        if "design" in respostas:
            resumo += f"- Estilo: {respostas['design']}\n"
        if "tipo" in respostas:
            resumo += f"- Tipo: {respostas['tipo']}\n"
        if "site_existente" in respostas:
            resumo += f"- Aplicação: {respostas['site_existente']}\n"
        if "exemplo" in respostas:
            resumo += f"- Exemplo: {respostas['exemplo']}\n"
        if "interatividade" in respostas:
            resumo += f"- Interatividade: {respostas['interatividade']}\n"
    elif serviço == "manutencao":
        resumo += "- Plano de manutenção\n"
        if "tipo_manutencao" in respostas:
            resumo += f"- Tipo: {respostas['tipo_manutencao']}\n"
        if "frequencia" in respostas:
            resumo += f"- Frequência: {respostas['frequencia']}\n"
        if "site_sistema" in respostas:
            resumo += f"- Site/Sistema: {respostas['site_sistema']}\n"
        if "problemas" in respostas:
            resumo += f"- Problemas: {respostas['problemas']}\n"
        if "monitoramento" in respostas:
            resumo += f"- Monitoramento: {respostas['monitoramento']}\n"

    ja_possui = ""
    if "dominio" in respostas and "não" not in respostas["dominio"].lower():
        ja_possui += f"- Domínio: {respostas['dominio']}\n"
    if "redes" in respostas and "nenhuma" not in respostas["redes"].lower():
        ja_possui += f"- Redes sociais: {respostas['redes']}\n"
    if "hospedagem" in respostas and "não" not in respostas["hospedagem"].lower():
        ja_possui += f"- Hospedagem: {respostas['hospedagem']}\n"
    if ja_possui:
        resumo += f"\nJá possui:\n{ja_possui}"

    resumo += f"Obrigado por compartilhar essas infos, {nome}! Pra montar uma proposta personalizada e alinhar os detalhes, o ideal é marcarmos uma reunião rápida com um especialista via Google Meet. Qual dia e horário você tem disponível?"
    
    await asyncio.sleep(random.uniform(5, 15))
    await update.message.chat.send_action(ChatAction.TYPING)
    await asyncio.sleep(1)
    await update.message.reply_text(resumo)
    user_data["orçamento"]["step"] = "reuniao"