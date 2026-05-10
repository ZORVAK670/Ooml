from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from replit import db
import time

TOKEN = "8482095863:AAEm78Ig4tfTuVvNjj9vAE0nb4NL06jKgJ0"
ADMIN_ID = 8600898029

# ---------- INIT DB ----------
if "warns" not in db:
    db["warns"] = {}

if "muted" not in db:
    db["muted"] = {}

if "logs" not in db:
    db["logs"] = []

BAD_WORDS = ["badword1", "badword2"]
MAX_WARN = 3

# ---------- LOG SYSTEM ----------
def log(event):
    logs = db["logs"]
    logs.append(f"{time.strftime('%H:%M:%S')} | {event}")
    db["logs"] = logs[-100:]

# ---------- WARN SYSTEM ----------
def add_warn(uid):
    warns = db["warns"]
    uid = str(uid)
    warns[uid] = warns.get(uid, 0) + 1
    db["warns"] = warns
    return warns[uid]

def reset_warn(uid):
    warns = db["warns"]
    warns.pop(str(uid), None)
    db["warns"] = warns

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡 Rose+ Advanced Bot Active")

# ---------- WELCOME ----------
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for u in update.message.new_chat_members:
        await update.message.reply_text(f"👋 Welcome {u.first_name} 🛡 Safe Group")

# ---------- MODERATION ENGINE ----------
async def engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.lower()
    uid = update.effective_user.id
    chat_id = update.effective_chat.id

    # mute check
    if str(uid) in db["muted"]:
        await update.message.delete()
        return

    # bad words
    for w in BAD_WORDS:
        if w in text:
            await update.message.delete()
            warn = add_warn(uid)
            log(f"WARN {uid} -> {warn}")

            if warn >= MAX_WARN:
                await context.bot.ban_chat_member(chat_id, uid)
                reset_warn(uid)
                log(f"AUTO BAN {uid}")
            return

    # spam links
    if "http" in text or "t.me" in text:
        await update.message.delete()
        warn = add_warn(uid)
        log(f"LINK SPAM {uid} -> {warn}")

# ---------- ADMIN: MUTE ----------
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        db["muted"][str(uid)] = True
        await update.message.reply_text("🔇 User muted")

# ---------- ADMIN: UNMUTE ----------
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        db["muted"].pop(str(uid), None)
        await update.message.reply_text("🔊 User unmuted")

# ---------- ADMIN: BAN ----------
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        await context.bot.ban_chat_member(update.effective_chat.id, uid)
        await update.message.reply_text("🚫 User banned")

# ---------- STATS ----------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        f"📊 ROSE+ STATS\n"
        f"⚠️ Warns: {len(db['warns'])}\n"
        f"🔇 Muted: {len(db['muted'])}\n"
        f"📜 Logs: {len(db['logs'])}"
    )

# ---------- RUN ----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("stats", stats))

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, engine))

app.run_polling()
