from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import random
import asyncio
from flask import Flask
from threading import Thread
import os

# Global Cancel System
cancel_users = {}

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ====================== PUT YOUR BOT TOKEN HERE ======================
BOT_TOKEN = "8728683065:AAGOKj9zxYDfv_xSy16UpMjz4gInwpG9WgQ"   # ←←← Change this
# =====================================================================

# ====================== HELPERS ======================

def check_luhn(card_number: str) -> bool:
    digits = [int(d) for d in card_number]
    checksum = 0
    is_even = False
    for digit in reversed(digits):
        if is_even:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
        is_even = not is_even
    return checksum % 10 == 0


def generate_random_digits(length: int) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def generate_card(bin_prefix: str, month: str = None, year: str = None, cvv: str = None):
    is_amex = bin_prefix.startswith(('34', '37'))
    total_length = 15 if is_amex else 16
    
    remaining = total_length - len(bin_prefix)
    card = bin_prefix + generate_random_digits(remaining)
    
    # Make sure it passes Luhn check
    while not check_luhn(card):
        card = bin_prefix + generate_random_digits(remaining)
    
    # Month
    if not month or month.lower() in ['none', 'random']:
        month = f"{random.randint(1, 12):02d}"
    
    # Year
    if not year or year.lower() in ['none', 'random']:
        year = str(random.randint(2026, 2035))
    elif len(year) == 2:
        year = "20" + year
    
    # CVV
    if not cvv or cvv.lower() in ['none', 'random']:
        if is_amex:
            cvv = str(random.randint(1000, 9999))
        else:
            cvv = str(random.randint(100, 999))
    
    return f"{card}|{month}|{year}|{cvv}"


# ====================== /gen COMMAND ======================

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id
    cancel_users[user_id] = False   # Initialize cancel flag

    try:
        user_input = ' '.join(context.args).strip() if context.args else ""
        
        if not user_input:
            await message.reply_text(
                "✿︎ **ᴜsᴀɢᴇ :**\n"
                "`/gen 519603`\n"
                "`/gen 519603 20`\n"
                "`/gen 519603|02|29`\n"
                "`/gen 519603|02|29 15`",
                parse_mode='Markdown'
            )
            return

        parts = user_input.split()
        bin_part = parts[0]
        amount = int(parts[1]) if len(parts) > 1 else 10

        # Handle BIN|MM|YY format
        mes = ano = cvv = None
        if "|" in bin_part:
            bin_exp = bin_part.split("|")
            bin_part = bin_exp[0]
            if len(bin_exp) > 1: mes = bin_exp[1]
            if len(bin_exp) > 2: ano = bin_exp[2]
            if len(bin_exp) > 3: cvv = bin_exp[3]

        if not bin_part or bin_part[0] not in '3456':
            await message.reply_text("✿︎ ʙɪɴ ᴍᴜsᴛ sᴛᴀʀᴛ ᴡɪᴛʜ 3, 4, 5, ᴏʀ 6 ")
            return

        if amount < 1:
            await message.reply_text("✿︎ ᴀᴍᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ ᴀᴛ ʟᴇᴀsᴛ 1")
            return

        if amount > 2000:
            await message.reply_text("✿︎ ᴍᴀxɪᴍᴜᴍ ʟɪᴍɪᴛ ɪs 2000 ᴄᴀʀᴅs!")
            return

        status = await message.reply_text(f"✿︎ ɢᴇɴᴇʀᴀᴛɪɴɢ {amount} ᴄᴄ's... ᴜsᴇ /ᴄᴀɴᴄᴇʟ ᴛᴏ sᴛᴏᴘ ᴛʜᴇ ᴘʀᴏᴄᴇss.", parse_mode='HTML')

        # Generate cards
        cards_list = []
        for i in range(amount):
            if cancel_users.get(user_id, False):
                await status.edit_text("❌ **ᴘʀᴏᴄᴇss ᴄᴀɴᴄᴇʟʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**")
                cancel_users.pop(user_id, None)
                return
            cards_list.append(generate_card(bin_part, mes, ano, cvv))

        cards_text = "\n".join(cards_list)

        # Send as TXT if more than 50
        if amount > 50:
            import io
            buf = io.BytesIO(cards_text.encode("utf-8"))
            buf.name = f"cc_gen_{bin_part}_{amount}.txt"
            
            await message.reply_document(
                document=buf,
                caption=f"✿ ᴄᴄ's ɢᴇɴᴇʀᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ\n"
                        f"✿ ʙɪɴ - {bin_part}\n"
                        f"✿ ᴛᴏᴛᴀʟ ᴀᴍᴏᴜɴᴛ - {amount}\n",
                parse_mode='HTML'
            )
        else:
            output = f"""<b>༺ ᴇɴᴊᴏʏ ᴍᴀxxɢᴇɴ 🐾 ༻</b>
━━━━━━━━━━━━━━━━━━━━━━━

✿ ᴄᴄ ɢᴇɴᴇʀᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ
✿ ʙɪɴ - {bin_part}
✿ ᴀᴍᴏᴜɴᴛ - {amount}

<code>{cards_text}</code>

✿ <b>ғʀᴇᴇ ᴄʜᴇᴄᴋᴇʀ:</b> @MaxxCHECKERbot"""

            await message.reply_text(output, parse_mode='HTML')

    except Exception as e:
        await message.reply_text(f"✿︎ ᴇʀʀᴏʀ: {str(e)}")
    finally:
        cancel_users.pop(user_id, None)   # Clean up

# ====================== /cancel COMMAND ======================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in cancel_users:
        cancel_users[user_id] = True
        await update.message.reply_text("❌ **ᴘʀᴏᴄᴇss ᴄᴀɴᴄᴇʟʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**", parse_mode='HTML')
    else:
        await update.message.reply_text("✅ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴘʀᴏᴄᴇss ᴛᴏ ᴄᴀɴᴄᴇʟ.", parse_mode='HTML')
    
async def splittxt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    cid = message.chat.id
    user_id = update.effective_user.id
    
    text = ' '.join(context.args).strip() if context.args else ""
    try:
        chunk_size = int(text) if text else 500
    except:
        chunk_size = 500

    if chunk_size < 1:
        await message.reply_text("❌ ᴄʜᴜɴᴋ sɪᴢᴇ ᴍᴜsᴛ ʙᴇ ᴀᴛʟᴇᴀsᴛ 1.", parse_mode='HTML')
        return

    reply = message.reply_to_message
    if not reply or not reply.document:
        await message.reply_text("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ <b>.ᴛxᴛ ғɪʟᴇ</b> ᴡɪᴛʜ ᴛʜɪs ᴄᴍᴅ.", parse_mode='HTML')
        return

    # Initialize cancel flag
    cancel_users[user_id] = False

    status = await message.reply_text("⏳ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ғɪʟᴇ...", parse_mode='HTML')

    try:
        file_id = reply.document.file_id
        file = await context.bot.get_file(file_id)
        data = await file.download_as_bytearray()
        
        try:
            file_text = data.decode("utf-8", errors="ignore")
        except:
            file_text = data.decode("latin-1", errors="ignore")

        all_lines = [line.strip() for line in file_text.splitlines() if line.strip()]
        total = len(all_lines)

        if total == 0:
            await status.edit_text("❌ ғɪʟᴇ ɪs ᴇᴍᴘᴛʏ.")
            return

        num_chunks = (total + chunk_size - 1) // chunk_size

        await status.edit_text(f"✂️ sᴘʟɪᴛᴛɪɴɢ <b>{total}</b> ʟɪɴᴇs...\nᴜsᴇ /ᴄᴀɴᴄᴇʟ ᴛᴏ sᴛᴏᴘ ᴛʜᴇ ᴘʀᴏᴄᴇss.", parse_mode='HTML')

        import io
        import asyncio

        for i in range(num_chunks):
            if cancel_users.get(user_id, False):
                await status.edit_text("🛑 **ᴘʀᴏᴄᴇss ᴄᴀɴᴄᴇʟʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**")
                cancel_users.pop(user_id, None)
                return

            start = i * chunk_size
            end = min(start + chunk_size, total)
            chunk_lines = all_lines[start:end]
            chunk_text = "\n".join(chunk_lines)
            
            buf = io.BytesIO(chunk_text.encode("utf-8"))
            buf.name = f"cards_part{i+1}_of_{num_chunks}.txt"
            
            await context.bot.send_document(cid, buf, caption=f"📄 ᴘᴀʀᴛ {i+1}/{num_chunks} — {len(chunk_lines)} ᴄᴀʀᴅs")
            
            if num_chunks > 3:
                await asyncio.sleep(0.4)

        await status.edit_text(f"✅ sᴜᴄᴄᴇssғᴜʟʟʏ sᴘʟɪᴛᴇᴅ <b>{total}</b> ᴄᴀʀᴅs ɪɴᴛᴏ <b>{num_chunks}</b> ғɪʟᴇs.", parse_mode='HTML')

    except Exception as e:
        await status.edit_text(f"❌ ᴇʀʀᴏʀ: {str(e)[:150]}")
    finally:
        cancel_users.pop(user_id, None)   # Clean up properly

# ====================== /start COMMAND ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """<b>༺ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴍᴀxxɢᴇɴ 🐾 ༻</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>✿︎ ᴍᴀxxɢᴇɴ ɢᴇɴᴇʀᴀᴛᴇs ʟᴜʜɴ-ᴠᴀʟɪᴅ ᴄᴀʀᴅs </b>

<b>📌 ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs:</b>

• <code>/gen<code> - ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀᴅs 
• <code>/splittxt<code> {ᴀᴍᴏᴜɴᴛ} - sᴘʟɪᴛ ғɪʟᴇ ɪɴᴛᴏ ᴄʜᴜɴᴋs

<b>⚙ ʜᴏᴡ ᴛᴏ ᴜsᴇ:</b>
• <code>/gen 519603</code> → ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀᴅs
• <code>/gen 519603 20</code> → ɢᴇɴᴇʀᴀᴛᴇ 20 ᴄᴀʀᴅs
• <code>/gen 519603|02|29</code> → ᴡɪᴛʜ ᴇxᴘɪʀʏ
• <code>/gen 519603|02|29 15</code> → ᴡɪᴛʜ ᴇxᴘɪʀʏ + ᴀᴍᴏᴜɴᴛ
• <ᴄᴏᴅᴇ>/splittxt<code> {ᴀᴍᴏᴜɴᴛ} → ʀᴇᴘʟʏ ᴛᴏ ᴀ .ᴛxᴛ ғɪʟᴇ

━━━━━━━━━━━━━━━━━━━━━━━
<b>ғʀᴇᴇ ᴄʜᴇᴄᴋᴇʀ:</b> @MaxxCHECKERbot 🐎""" 

    await update.message.reply_text(welcome_text, parse_mode='HTML') 
    
    
# ====================== MAIN FOR RENDER ======================

if __name__ == "__main__":
    print("✅ Starting MaxxGen Bot...")

    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("splittxt", splittxt))
    app.add_handler(CommandHandler("cancel", cancel))
    
    print("✅ Bot is running... (Render Mode)")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        poll_interval=3
        )
