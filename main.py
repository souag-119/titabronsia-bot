import os
import sys
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio


# ---- Flask web (لـ UptimeRobot و Render) ----
app = Flask(__name__)


@app.route("/")
def home():
return "Titabronsia Bot is alive!"


def run_web():
port = int(os.environ.get("PORT", 8080))
# تشغيل خفيف للويب server؛ Render يزوّد PORT تلقائياً
app.run(host="0.0.0.0", port=port, threaded=True)


def keep_alive():
t = Thread(target=run_web, daemon=True)
t.start()


# ---- Discord bot ----
# اقرأ المتغير من DISCORD_TOKEN وإلا من TOKEN (مرونة)
TOKEN = os.environ.get("DISCORD_TOKEN") or os.environ.get("TOKEN")
if not TOKEN:
print("❌ خطأ: لم أجد متغير البيئة DISCORD_TOKEN أو TOKEN. ضعه في settings على Render ثم أعد النشر.")
sys.exit(1)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix="!", intents=intents)


# عدّل القيم هذه حسب السيرفر والرتبة عندك
GUILD_ID = 1241372550198460487
ROLE_ID = 1264593302137733180


# مجموعة مؤقتة لمنع سبام النقر من نفس المستخدم
processing = set()


class WelcomeView(discord.ui.View):
def __init__(self):
super().__init__(timeout=None)


@discord.ui.button(label="✅ أوافق على الدخول", style=discord.ButtonStyle.success, custom_id="accept_entry")
async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
member = interaction.user
guild = interaction.guild
role = guild.get_role(ROLE_ID)


# منع السبام لنفس العضو
if member.id in processing:
await interaction.response.send_message("⏳ جاري المعالجة — انتظر لحظة ثم حاول مرة أخرى.", ephemeral=True)
return


processing.add(member.id)
try:
raise
