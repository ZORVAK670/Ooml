from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from replit import db

# ================= CONFIG =================
TOKEN = "8482095863:AAEm78Ig4tfTuVvNjj9vAE0nb4NL06jKgJ0"
ADMIN_ID = 8600898029

# ================= DATABASE =================
if "balance" not in db:
    db["balance"] = {}

if "tasks" not in db:
    db["tasks"] = [
        "https://t.me/oq_pubg_store",
        "https://t.me/ooq_store",
        "https://t.me/EasyEarnAppBot?start=ref_8600898029",
        "https://t.me/easyearnofficial1222",
        "https://t.me/easyearnpayments"
    ]

# ================= APP MENU =================
def menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💰 Wallet", callback_data="bal"),
            InlineKeyboardButton("📢 Tasks", callback_data="task")
        ],
        [
            InlineKeyboardButton("➕ Submit Task", callback_data="submit"),
            InlineKeyboardButton("🔗 Referral", callback_data="ref")
        ],
        [
            InlineKeyboardButton("📊 Leaderboard", callback_data="board")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="lang")
        ]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    db["balance"].setdefault(uid, 0)

    await update.message.reply_text(
        "🚀 Welcome to OQ App Bot\n\nSelect option below:",
        reply_markup=menu()
    )

# ================= CALLBACK =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = str(q.from_user.id)

    await q.answer()

    # 💰 WALLET
    if q.data == "bal":
        await q.message.edit_text(
            f"💰 WALLET\n\nBalance: {db['balance'].get(uid,0)} coins",
            reply_markup=menu()
        )

    # 📢 TASKS
    elif q.data == "task":
        tasks = db["tasks"]

        text = "📢 TASK LIST:\n\n"

        for t in tasks:
            text += f"👉 {t}\n"

        text += "\n💰 Reward: +0.5 coins per task"

        await q.message.edit_text(text, reply_markup=menu())

    # 🔗 REFERRAL
    elif q.data == "ref":
        link =https://t.me/Anti_zorvak_bot?start={uid}"

        await q.message.edit_text(
            f"🔗 REFERRAL LINK:\n{link}\n\n💰 Earn +2 coins per invite",
            reply_markup=menu()
        )

    # ➕ SUBMIT
    elif q.data == "submit":
        if db["balance"].get(uid,0) < 30:
            await q.message.edit_text("❌ Need 30 coins", reply_markup=menu())
        else:
            await q.message.edit_text("📩 Use: /submit @channel", reply_markup=menu())

    # ⚙️ SETTINGS
    elif q.data == "lang":
        await q.message.edit_text(
            "⚙️ SETTINGS\n\nChoose language:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🇦🇫 پښتو", callback_data="ps"),
                    InlineKeyboardButton("🇮🇷 دری", callback_data="fa"),
                    InlineKeyboardButton("🇬🇧 English", callback_data="en")
                ]
            ])
        )

    elif q.data in ["ps","fa","en"]:
        await q.message.edit_text("✅ Language updated", reply_markup=menu())

# ================= DONE TASK =================
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    db["balance"][uid] = db["balance"].get(uid,0) + 0.5

    await update.message.reply_text("✅ +0.5 coins earned")

# ================= SUBMIT TASK =================
async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    if db["balance"].get(uid,0) < 30:
        await update.message.reply_text("❌ Need 30 coins")
        return

    if not context.args:
        await update.message.reply_text("Use: /submit @channel")
        return

    link = context.args[0]

    db["tasks"].append(link)
    db["balance"][uid] = 0

    await update.message.reply_text("✅ Task added successfully")

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("submit", submit))
app.add_handler(CommandHandler("done", done))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
