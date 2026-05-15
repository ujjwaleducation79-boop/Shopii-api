from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import random
import asyncio

# ====================== PUT YOUR BOT TOKEN HERE ======================
BOT_TOKEN = "8728683065:AAELQYTfpIYECGox5y8J63Hrdr8iy1Sb584"   # ←←← Change this
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
    try:
        message = update.message
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

        # Validation
        if not bin_part or bin_part[0] not in '3456':
            await message.reply_text("✿︎ ʙɪɴ ᴍᴜsᴛ sᴛᴀʀᴛ ᴡɪᴛʜ 3, 4, 5, ᴏʀ 6 ")
            return

        if amount < 1 or amount > 100:
            await message.reply_text("✿︎ ᴛʀʏ ᴏɴʟʏ 100 ᴄᴄ's ᴀᴛ ᴀ ᴛɪᴍᴇ!")
            return

        if len(bin_part) > 16:
            await message.reply_text("✿︎ ʙɪɴ ᴛᴏᴏ ʟᴏɴɢ ᴛʀʏ ᴜɴᴅᴇʀ 16!")
            return

        # Generate cards
        cards_list = [generate_card(bin_part, mes, ano, cvv) for _ in range(amount)]
        cards_text = "\n".join(cards_list)

        output = f"""<b>༺ ᴇɴᴊᴏʏ ᴍᴀxxɢᴇɴ 🐾 ༻</b>
━━━━━━━━━━━━━━━━━━━━━━━

✿ ᴄᴄ ɢᴇɴᴇʀᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ
✿ ʙɪɴ - {bin_part}
✿ ᴀᴍᴏᴜɴᴛ - {amount}

<code>{cards_text}</code>

✿ <b>ғʀᴇᴇ ᴄʜᴇᴄᴋᴇʀ:</b> @MaxxCHECKERbot"""

        await message.reply_text(output, parse_mode='HTML')

    except Exception as e:
        await message.reply_text(f"✿︎ Error: {str(e)}")


# ====================== /start COMMAND ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """<b>༺ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴍᴀxxɢᴇɴ 🐾 ༻</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>✿︎ ᴍᴀxxɢᴇɴ ɢᴇɴᴇʀᴀᴛᴇs ʟᴜʜɴ-ᴠᴀʟɪᴅ ᴄᴀʀᴅs </b>

<b>📌 ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs:</b>
• /gen - ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀᴅs

<b>⚙ ʜᴏᴡ ᴛᴏ ᴜsᴇ:</b>
• <code>/gen 519603</code> → ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀᴅs
• <code>/gen 519603 20</code> → ɢᴇɴᴇʀᴀᴛᴇ 20 ᴄᴀʀᴅs
• <code>/gen 519603|02|29</code> → ᴡɪᴛʜ ᴇxᴘɪʀʏ
• <code>/gen 519603|02|29 15</code> → ᴡɪᴛʜ ᴇxᴘɪʀʏ + ᴀᴍᴏᴜɴᴛ

━━━━━━━━━━━━━━━━━━━━━━━
<b>ғʀᴇᴇ ᴄʜᴇᴄᴋᴇʀ:</b> @MaxxCHECKERbot 🐎""" 

    await update.message.reply_text(welcome_text, parse_mode='HTML') 

# ====================== MAIN ======================

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    
    print("✅ Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
