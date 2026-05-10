from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from replit import db

# ================= CONFIG =================
TOKEN = "8482095863:AAEm78Ig4tfTuVvNjj9vAE0nb4NL06jKgJ0"

ADMIN_ID = 8600898029

CHANNEL = "@oq_pubg_store"
GROUP = "@ooq_store"

# ================= DB =================
if "balance" not in db:
    db["balance"] = {}

if "tasks" not in db:
    db["tasks"] = []

if "lang" not in db:
    db["lang"] = {}

# ================= APP MENU =================
def menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Wallet", callback_data="bal"),
            InlineKeyboardButton("📢 Tasks", callback_data="task")
        ],
        [
            InlineKeyboardButton("➕ Submit", callback_data="submit"),
            InlineKeyboardButton("🔗 Referral", callback_data="ref")
        ],
        [
            InlineKeyboardButton("⚙️ Language", callback_data="lang")
        ]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    db["balance"].setdefault(uid, 0)
    db["lang"].setdefault(uid, "ps")

    await update.message.reply_text(
        "🚀 Welcome to OQ App Bot\n\nChoose option:",
        reply_markup=menu()
    )

# ================= CALLBACK =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = str(q.from_user.id)

    await q.answer()

    # WALLET
    if q.data == "bal":
        await q.message.edit_text(
            f"💰 WALLET\n\nBalance: {db['balance'].get(uid,0)} coins",
            reply_markup=menu()
        )

    # TASKS
    elif q.data == "task":
        if not db["tasks"]:
            await q.message.edit_text("📢 No tasks available", reply_markup=menu())
            return

        t = db["tasks"][0]

        await q.message.edit_text(
            f"📢 TASK\n\nJoin:\n{t['link']}\n\n💰 +2 coins",
            reply_markup=menu()
        )

    # REFERRAL
    elif q.data == "ref":
        link = f"https://t.me/YOUR_BOT_USERNAME?start={uid}"

        await q.message.edit_text(
            f"🔗 REFERRAL LINK\n\n{link}\n\nInvite = +2 coins",
            reply_markup=menu()
        )

    # SUBMIT
    elif q.data == "submit":
        if db["balance"].get(uid,0) < 30:
            await q.message.edit_text("❌ Need 30 coins", reply_markup=menu())
        else:
            await q.message.edit_text("📩 Send: /submit @channel")

    # LANGUAGE
    elif q.data == "lang":
        await q.message.edit_text(
            "⚙️ Choose Language",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🇦🇫 پښتو", callback_data="ps"),
                    InlineKeyboardButton("🇮🇷 دری", callback_data="fa"),
                    InlineKeyboardButton("🇬🇧 English", callback_data="en")
                ]
            ])
        )

    elif q.data in ["ps","fa","en"]:
        db["lang"][uid] = q.data
        await q.message.edit_text("✅ Updated", reply_markup=menu())

# ================= TASK COMPLETE =================
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    db["balance"][uid] = db["balance"].get(uid,0) + 2

    if db["tasks"]:
        db["tasks"].pop(0)

    await update.message.reply_text("✅ +2 coins earned")

# ================= SUBMIT =================
async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if db["balance"].get(uid,0) < 30:
        await update.message.reply_text("❌ Need 30 coins")
        return

    if not context.args:
        await update.message.reply_text("Use: /submit @channel")
        return

    link = context.args[0]

    db["tasks"].append({
        "link": link,
        "owner": uid
    })

    db["balance"][uid] = 0

    await update.message.reply_text("✅ Added to task pool")

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("submit", submit))
app.add_handler(CommandHandler("done", done))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
