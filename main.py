from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from replit import db

# ================= CONFIG =================
TOKEN = "8482095863:AAEm78Ig4tfTuVvNjj9vAE0nb4NL06jKgJ0"

ADMIN_ID = 8600898029

HELP_USERNAME = "@oq_Zorvak"
CHANNEL_LINK = "https://t.me/oq_pubg_store"
GROUP_LINK = "https://t.me/ooq_store"

# ================= DATABASE =================
if "users" not in db:
    db["users"] = {}

if "balance" not in db:
    db["balance"] = {}

if "lang" not in db:
    db["lang"] = {}

if "tasks" not in db:
    db["tasks"] = []

# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Balance", callback_data="bal"),
         InlineKeyboardButton("🔗 Referral", callback_data="ref")],

        [InlineKeyboardButton("➕ Submit", callback_data="submit"),
         InlineKeyboardButton("📞 Help", callback_data="help")],

        [InlineKeyboardButton("🌐 Language", callback_data="lang")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    db["users"][uid] = True
    db["balance"].setdefault(uid, 0)
    db["lang"].setdefault(uid, "ps")

    await update.message.reply_text(
        "🚀 Welcome to Promo Bot",
        reply_markup=menu()
    )

# ================= BUTTON HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = str(q.from_user.id)
    await q.answer()

    db["balance"].setdefault(uid, 0)

    # BALANCE
    if q.data == "bal":
        await q.message.edit_text(
            f"💰 Balance: {db['balance'][uid]} coins",
            reply_markup=menu()
        )

    # REFERRAL
    elif q.data == "ref":
        link = f"https://t.me/YOUR_BOT_USERNAME?start={uid}"
        await q.message.edit_text(
            f"🔗 Invite Link:\n{link}\n\n👥 Invite = +2 coins",
            reply_markup=menu()
        )

    # HELP
    elif q.data == "help":
        await q.message.edit_text(
            f"📞 Help: {HELP_USERNAME}\n\n"
            f"📢 Channel: {CHANNEL_LINK}\n"
            f"👥 Group: {GROUP_LINK}",
            reply_markup=menu()
        )

    # SUBMIT
    elif q.data == "submit":
        if db["balance"][uid] < 30:
            await q.message.edit_text(
                "❌ Need 30 coins first",
                reply_markup=menu()
            )
        else:
            await q.message.edit_text("📩 Send: /submit @channel")

# ================= TASK SYSTEM =================
async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    db["balance"][uid] = db["balance"].get(uid, 0) + 2

    await update.message.reply_text("✅ +2 coins earned!")

# ================= SUBMIT CHANNEL =================
async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if db["balance"].get(uid, 0) < 30:
        await update.message.reply_text("❌ Not enough coins (30 required)")
        return

    if not context.args:
        await update.message.reply_text("Use: /submit @channel")
        return

    channel = context.args[0]

    db["tasks"].append({
        "channel": channel,
        "owner": uid
    })

    db["balance"][uid] = 0  # reset after submission

    await update.message.reply_text(
        "✅ Channel added to task pool!"
    )

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("task", task))
app.add_handler(CommandHandler("submit", submit))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
