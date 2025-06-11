import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread
import asyncio  # ← أضفنا هذا للسليب

# إعداد Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Titabronsia Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# إعداد Discord Bot
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1241372550198460487  # ← ضع ID السيرفر
ROLE_ID = 1264593302137733180   # ← ضع ID الرتبة

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ أوافق على الدخول", style=discord.ButtonStyle.success, custom_id="accept_entry")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(ROLE_ID)
        if role:
            await asyncio.sleep(1)  # ← تأخير بسيط لتجنب Too Many Requests
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                "✨ تم قبولك بنجاح! مرحبًا بك في Titabronsia.",
                ephemeral=True
            )
            print(f"🟢 {interaction.user} حصل على الرتبة.")
        else:
            await interaction.response.send_message("❌ لم يتم العثور على الرتبة.", ephemeral=True)
            print("🔴 لم يتم العثور على الرتبة.")

@bot.event
async def on_ready():
    print(f"✅ البوت {bot.user} جاهز")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ تمت مزامنة {len(synced)} أمر Slash.")
    except Exception as e:
        print(f"❌ خطأ أثناء المزامنة: {e}")

@bot.tree.command(name="setwelcome", description="يرسل رسالة الترحيب", guild=discord.Object(id=GUILD_ID))
async def setwelcome(interaction: discord.Interaction):
    embed = discord.Embed(
        title="مرحبًا بك في Titabronsia...",
        description=(
            "عالم خيالي لا تصل إليه الأرجل، بل تهمس لك البوابة القديمة باسمه في لحظة شرود.\n"
            "هنا، تتلاشى حدود الواقع، وتنبض الأرض بقوانينها الخاصة...\n"
            "خلف النسيج الكوني، تحكم نواة النُظم هذا العالم، وتراقب كل من يعبر إلى الداخل.\n\n"
            "**هل أنت زائر عابر؟ أم روح تنتمي للتيار الخفي؟**\n\n"
            "📜 قبل أن تخطو أعمق في هذا العالم، تأكد من قراءة القوانين داخل بوابة النظام.\n"
            "فكما أن الضوء يحكم النهار، تحكم القوانين Titabronsia.\n\n"
            "✨ كن محترمًا، متعاونًا، ومبدعًا. شارك، استمتع، ولا تتردد في ترك بصمتك.\n"
            "فالعالم هنا لا يكتمل إلا بمن يعبرونه... مثلك.\n\n"
            "🔔 عند جاهزيتك، افتح البوابة عبر الزر أدناه، وانضم رسميًا إلى أعماق Titabronsia.\n\n"
            "شارك في فعاليات خيالية، مثّل رولاتك، واندمج في محاكاة هذا الكون الغريب.\n\n"
            "**Titabronsia ليست مجرد سيرفر...**\n"
            "إنها شظية من عالم آخر تنتظر من يُعيد تشكيلها.\n\n"
            "**هل تجرؤ على الدخول؟**"
        ),
        color=discord.Color.purple()
    )

    await interaction.response.send_message(embed=embed, view=WelcomeView())

# تشغيل السيرفر + البوت
keep_alive()
bot.run(TOKEN)
