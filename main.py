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
            # تحقق سريع إن العضو لديه الدور
            if role in member.roles:
                await interaction.response.send_message("❗ لديك هذه الرتبة بالفعل.", ephemeral=True)
                return

            # رد سريع لتفادي timeout
            await interaction.response.defer(ephemeral=True, thinking=True)

            # تأخير بسيط لحماية من السبام الكثيف
            await asyncio.sleep(1)

            try:
                await member.add_roles(role)
                await interaction.followup.send("✨ تم قبولك بنجاح! مرحبًا بك في Titabronsia.", ephemeral=True)
                print(f"🟢 {member} حصل على الرتبة.")
            except discord.Forbidden:
                await interaction.followup.send("❌ لا أملك صلاحية Manage Roles أو موقعي أقل من الرتبة. تواصل مع الإدارة.", ephemeral=True)
                print("❌ Forbidden: البوت لا يملك صلاحية Manage Roles أو موقعه أقل من الرتبة.")
            except discord.HTTPException as e:
                await interaction.followup.send("❌ حدث خطأ مؤقت مع خوادم Discord. حاول لاحقًا.", ephemeral=True)
                print("❌ HTTPException عند add_roles:", e)

        finally:
            if member.id in processing:
                processing.remove(member.id)


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


# ---- شغّل الويب ثم البوت ----
keep_alive()

try:
    bot.run(TOKEN)
except Exception as e:
    print("❌ فشل تشغيل البوت:", e)
    raise

import discord
from discord.ext import commands, tasks
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

guild_states = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def bedtime(ctx, hours: float = None):
    guild = ctx.guild

    if guild.id in guild_states:
        await ctx.send("⚠️ وضع النوم مفعل بالفعل. استعمل !wake لإيقافه.")
        return

    prev_perms = {}
    for member in guild.members:
        if member.guild_permissions.administrator:
            continue
        prev_perms[member.id] = {}
        for channel in guild.channels:
            try:
                prev_perms[member.id][channel.id] = channel.overwrites_for(member)
                await channel.set_permissions(member, view_channel=False)
            except Exception as e:
                print(f"❌ خطأ مع {member} في {channel}: {e}")

    bedtime_channel = await guild.create_text_channel("حان وقت النوم")
    for member in guild.members:
        if member.guild_permissions.administrator:
            await bedtime_channel.set_permissions(member, view_channel=True, send_messages=True)
        else:
            await bedtime_channel.set_permissions(member, view_channel=True, send_messages=False)

    await bedtime_channel.send("اذهبوا للنوم")

    @tasks.loop(seconds=20)
    async def spam_message():
        try:
            await bedtime_channel.send("اذهبوا للنوم")
        except:
            pass

    spam_message.start()

    guild_states[guild.id] = {
        "prev_perms": prev_perms,
        "bedtime_channel": bedtime_channel,
        "task": spam_message
    }

    msg = "🌙 تم تفعيل وضع النوم!"
    if hours:
        msg += f" سوف يستمر {hours} ساعة ثم يستيقظ تلقائياً."
        async def auto_wake():
            await asyncio.sleep(int(hours * 3600))  # تحويل الساعات لثواني
            if guild.id in guild_states:
                channel = guild.text_channels[0]
                await wake(channel, auto=True)
        bot.loop.create_task(auto_wake())

    await ctx.send(msg)


@bot.command()
@commands.has_permissions(administrator=True)
async def wake(ctx, auto: bool = False):
    guild = ctx.guild
    if guild.id not in guild_states:
        if not auto:
            await ctx.send("⚠️ وضع النوم غير مفعل.")
        return

    state = guild_states[guild.id]
    state["task"].cancel()

    try:
        await state["bedtime_channel"].delete()
    except:
        pass

    for member_id, ch_data in state["prev_perms"].items():
        member = guild.get_member(member_id)
        if not member:
            continue
        for ch_id, perms in ch_data.items():
            channel = guild.get_channel(ch_id)
            if channel:
                try:
                    await channel.set_permissions(member, overwrite=perms)
                except Exception as e:
                    print(f"❌ خطأ استرجاع {member} في {channel}: {e}")

    del guild_states[guild.id]
    if not auto:
        await ctx.send("🌞 تم إلغاء وضع النوم وإرجاع كل شيء طبيعي.")
    else:
        await ctx.send("⏰ انتهى وقت النوم تلقائياً وتم إرجاع الوضع الطبيعي.")
