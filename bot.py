import os
import asyncio
import datetime
import requests
import base64
import json
import base64
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, ChatJoinRequest
from dotenv import load_dotenv

from database import get_session, UserAccess
from efipay import EfiPay



# ======= CONFIG =======
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK")
GN_CLIENT_ID = os.getenv("GN_CLIENT_ID")
GN_CLIENT_SECRET = os.getenv("GN_CLIENT_SECRET")
PIX_CHAVE = os.getenv("PIX_CHAVE")
#CERTIFICADO = os.getenv("CERTIFICADO")
GN_SANDBOX = os.getenv("GN_SANDBOX")

CERTIFICADO = "/etc/secrets/certificadoPROD3.pem"
credentials = {
    'client_id': GN_CLIENT_ID,
    'client_secret': GN_CLIENT_SECRET,
    'sandbox': False,
    'certificate': CERTIFICADO
}

efi = EfiPay(credentials)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

ADMINS = [123456789]  # Coloque seu ID admin aqui!

PLANOS = {
    "7dias": {"dias": 7, "preco": 15.00},
    "30dias": {"dias": 30, "preco": 25.00},
    "3meses": {"dias": 90, "preco": 65.00},
}

# ======= MENUS =======
def get_main_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton(text="💸 Assinar", callback_data="menu_assinar")],
        [InlineKeyboardButton(text="📊 Status", callback_data="menu_status")],
        [InlineKeyboardButton(text="❓ Ajuda", callback_data="menu_ajuda")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="⚙️ Administração", callback_data="menu_admin")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔓 Liberar acesso", callback_data="admin_liberar")],
            [InlineKeyboardButton(text="🚫 Remover acesso", callback_data="admin_remover")],
            [InlineKeyboardButton(text="📋 Listar clientes", callback_data="admin_listar")],
            [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_main")]
        ]
    )

# ======= GERENCIANET PIX =======
def criar_cobranca(valor):
    try:
        payload = {
            "calendario": {"expiracao": 3600},
            "valor": {"original": f"{float(valor):.2f}"},  # garante formato correto
            "chave": PIX_CHAVE,
            "solicitacaoPagador": "Pagamento do teste",
        }

        cobranca = efi.pix_create_immediate_charge(body=payload)
        return cobranca

    except Exception as e:
        print("Erro ao criar cobrança:", e)
        return {"erro": str(e)}

def gerar_qrcode(loc_id):
        qrcode = efi.pix_generate_qrcode(params={"id": loc_id})
        #print("QR Code gerado:", json.dumps(qrcode, indent=2))
        return qrcode

def base64_para_inputfile(imagem_base64, nome_arquivo="qrcode.png"):
    if "," in imagem_base64:
        imagem_base64 = imagem_base64.split(",")[1]
    imagem_bytes = base64.b64decode(imagem_base64)
    buffer = BytesIO(imagem_bytes)
    buffer.seek(0)
    
    # Aqui criamos o InputFile do jeito que o aiogram 3.x aceita
    return InputFile(file=buffer, filename=nome_arquivo)

async def verificar_pagamento(txid, user_id, dias, bot):
    tempo_limite = 3600  # 1 hora em segundos
    intervalo = 30       # Verifica a cada 30 segundos
    tempo_passado = 0

    while tempo_passado < tempo_limite:
        try:
            params = {
                'txid': txid
            }
            response =  efi.pix_detail_charge(params=params)
            status = response.get("status")

            if status == "CONCLUIDA":
                # Atualiza o banco de dados
                session = next(get_session())
                try:
                    user = session.query(UserAccess).filter_by(telegram_id=user_id).first()
                    if user:
                        user.is_paid_client = True
                        user.subscription_expiration = datetime.datetime.now() + datetime.timedelta(days=dias)
                        session.commit()
                finally:
                    session.close()

                # Envia o link do grupo
                await bot.unban_chat_member(GROUP_ID, user_id)
                await bot.send_message(
                    user_id,
                    f"✅ Pagamento confirmado!\n\n"
                    f"🏆 Parabens por adquirir esse plano, certeza que você vai gozar muito... opa gostar muito rs.\n\n"
                    f"🔗 Link do grupo: {GROUP_INVITE_LINK}"
                )
                break
            else:
                print(f"Status atual do Pix ({txid}): {status}")

        except Exception as e:
            print(f"Erro ao verificar pagamento: {e}")

        # Aguarda próximo ciclo de verificação
        await asyncio.sleep(intervalo)
        tempo_passado += intervalo
        
    if tempo_passado >= tempo_limite:
        await bot.send_message(
            user_id,
            "⚠️ O tempo para pagamento expirou (1 hora). Por favor, gere um novo Pix para continuar."
        )
# ======= /start =======
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    session = next(get_session())
    try:
        user = session.query(UserAccess).filter_by(telegram_id=m.from_user.id).first()
        if not user:
            user = UserAccess(
                telegram_id=m.from_user.id,
                full_name=m.from_user.full_name
            )
            session.add(user)
            session.commit()
    finally:
        session.close()

    is_admin = m.from_user.id in ADMINS
    await m.answer(
        f"👋 Bem-vindo, {m.from_user.full_name}!\n"
        "\n"
        "🔞 Aqui você vai encontar os melhores videos que existem na internet, por um preço extremamente baixo\n"
        "\n"
        "Use os botões abaixo:", 
        reply_markup=get_main_menu(is_admin))

# ======= CALLBACK =======
@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    data = call.data
    user_id = call.from_user.id

    if data == "menu_assinar":
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💸 7 dias - R$15", callback_data="plano_7dias")],
                [InlineKeyboardButton(text="💸 30 dias - R$25", callback_data="plano_30dias")],
                [InlineKeyboardButton(text="💸 90 dias - R$65", callback_data="plano_3meses")],
                [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_main")]
            ]
        )
        await call.message.edit_text("📌 Escolha um dos planos abaixo:", reply_markup=markup)

    elif data.startswith("plano_"):
        plano_key = data.split("_")[1]
        plano = PLANOS.get(plano_key)
        if not plano:
            await call.message.answer("Plano inválido.")
            return

        valor = plano["preco"]
        dias = plano["dias"]

        cobranca = criar_cobranca(valor)
        txid = cobranca.get("txid")
        print(txid)
        loc_id = cobranca.get("loc", {}).get("id")
        qrcode = gerar_qrcode(loc_id)
        imagem_qrcode = qrcode["imagemQrcode"]
        copia_cola = cobranca["pixCopiaECola"]
        ##foto_qrcode = base64_para_inputfile(qrcode["imagemQrcode"])

        await call.message.delete()  # Apaga mensagem anterior

        await bot.send_message(
            user_id,
            f"✅ Seu pedido foi gerado com sucesso!!\n\n"
            f"💦 O pedido escolhido foi: {plano.get('dias')} dias.\n"
            f"💰 Valor: R${valor:.2f}\n\n"
            f"👇 Copie o código abaixo para pagar:\n\n"
            f"<blockquote><code>{copia_cola}</code> </blockquote>\n\n"
            f"💥 Apos o pagamento, seu acesso sera liberado imediatamente e lhe enviaremos o link, tudo isso sem a necessidade de um ADM. Tudo rapido e facil.",
            parse_mode="HTML"
        )
        asyncio.create_task(verificar_pagamento(txid, user_id, dias, bot))

    elif data == "menu_status":
        session = next(get_session())
        try:
            user = session.query(UserAccess).filter_by(telegram_id=user_id).first()
            if not user:
                await call.message.edit_text("❌ Você não está registrado.", reply_markup=get_main_menu())
                return
            status = "✅ Ativo" if user.is_paid_client else "❌ Inativo"
            expiracao = user.subscription_expiration.strftime("%d/%m/%Y %H:%M") if user.subscription_expiration else "N/A"
            await call.message.edit_text(
                f"Status: {status}\nExpira em: {expiracao}",
                reply_markup=get_main_menu(user_id in ADMINS)
            )
        finally:
            session.close()

    elif data == "menu_ajuda":
        await call.message.edit_text(
            "ℹ️ Ajuda:\n- Use **Assinar** para escolher seu plano\n- Use **Status** para ver sua assinatura.",
            reply_markup=get_main_menu(user_id in ADMINS)
        )

    elif data == "menu_admin" and user_id in ADMINS:
        await call.message.edit_text("⚙️ Painel Administrativo:", reply_markup=get_admin_menu())

    elif data == "admin_listar" and user_id in ADMINS:
        session = next(get_session())
        try:
            ativos = session.query(UserAccess).filter_by(is_paid_client=True).all()
            if not ativos:
                msg = "Nenhum cliente ativo."
            else:
                msg = "👥 Clientes ativos:\n" + "\n".join([f"{u.full_name} | expira: {u.subscription_expiration.strftime('%d/%m/%Y')}" for u in ativos])
            await call.message.edit_text(msg, reply_markup=get_admin_menu())
        finally:
            session.close()

    elif data == "menu_main":
        is_admin = user_id in ADMINS
        await call.message.edit_text("Menu principal:", reply_markup=get_main_menu(is_admin))

    await call.answer()

def usuario_tem_pagamento_ativo(user_id):
    """
    Verifica no banco de dados se o usuário tem um pagamento ativo.
    Retorna True ou False.
    """
    session = next(get_session())
    usuario = session.query(UserAccess).filter_by(telegram_id=user_id).first()
    session.close()
    
    return bool(usuario and usuario.is_paid_client)

@dp.chat_join_request()
async def aprovar_entrada(update: ChatJoinRequest):
    user_id = update.from_user.id
    username = update.from_user.username

    try:
        if usuario_tem_pagamento_ativo(user_id):
            # Aprova automaticamente
            await bot.approve_chat_join_request(GROUP_ID, user_id)
            await bot.send_message(
                user_id,
                f"✅ Olá {username or 'usuário'}! Sua entrada no grupo foi aprovada. Bem-vindo(a)!"
            )
        else:
            # Rejeita se não houver pagamento
            await bot.decline_chat_join_request(GROUP_ID, user_id)
            await bot.send_message(
                user_id,
                "❌ Você ainda não possui pagamento ativo. Finalize o pagamento para ter acesso."
            )

    except Exception as e:
        print(f"Erro ao aprovar entrada de {user_id}: {e}")

# ======= VERIFICADOR =======
async def verificar_expiracoes():
    while True:
        now = datetime.datetime.now()
        session = next(get_session())
        try:
            expirados = session.query(UserAccess).filter(
                UserAccess.is_paid_client == True,
                UserAccess.subscription_expiration != None,
                UserAccess.subscription_expiration < now
            ).all()

            for user in expirados:
                user.is_paid_client = False
                session.commit()

                try:
                    await bot.ban_chat_member(GROUP_ID, user.telegram_id)
                except Exception as e:
                    print(f"Erro ao remover: {e}")

                try:
                    await bot.send_message(
                        user.telegram_id,
                        "⚠️ Sua assinatura expirou. Para continuar, renove seu pagamento!"
                    )
                except Exception as e:
                    print(f"Erro ao enviar mensagem: {e}")
        finally:
            session.close()

        await asyncio.sleep(86400)  # 24h

# ======= MAIN =======
async def main():
    asyncio.create_task(verificar_expiracoes())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
