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

# main.py (مُحدّث) — انسخ هذا الملف مكان القديم أو ادمجه
import os
import sys
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import asyncio
import datetime
from typing import Optional

# ---- Flask web (لـ UptimeRobot و Render) ----
app = Flask(__name__)

@app.route("/")
def home():
    return "Titabronsia Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, threaded=True)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

# ---- Discord bot ----
TOKEN = os.environ.get("DISCORD_TOKEN") or os.environ.get("TOKEN")
if not TOKEN:
    print("❌ خطأ: لم أجد متغير البيئة DISCORD_TOKEN أو TOKEN. ضعه في settings على Render ثم أعد النشر.")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # مهم: فعّل Server Members Intent في Developer Portal أيضاً

bot = commands.Bot(command_prefix="!", intents=intents)

# عدّل القيم هذه حسب سيرفرك التجريبي (نحن نستخدمها لمزامنة أوامر الـ slash سريعًا في سيرفرك)
GUILD_ID = 1241372550198460487
ROLE_ID = 1264593302137733180

# حالة السيرفر (تخزين بيانات النوم لكل جيلد)
# كل مفتاح = guild.id، القيمة = dict يحتوي prev_overwrites, bedtime_channel_id, spam_task, fallback_role_used, ...
guild_states: dict[int, dict] = {}

# مجموعة مؤقتة لمنع سبام النقر من نفس المستخدم (خاص بالـ WelcomeView)
processing = set()

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ أوافق على الدخول", style=discord.ButtonStyle.success, custom_id="accept_entry")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild
        role = guild.get_role(ROLE_ID)

        if member.id in processing:
            await interaction.response.send_message("⏳ جاري المعالجة — انتظر لحظة ثم حاول مرة أخرى.", ephemeral=True)
            return

        processing.add(member.id)
        try:
            if role in member.roles:
                await interaction.response.send_message("❗ لديك هذه الرتبة بالفعل.", ephemeral=True)
                return

            await interaction.response.defer(ephemeral=True, thinking=True)
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
    # نحاول مزامنة أوامر الـ slash:
    try:
        # مزامنة عالمية (قد تستغرق وقتاً لتظهر في كل السيرفرات)
        synced = await bot.tree.sync()
        print(f"✅ تمت مزامنة (global) {len(synced)} أمر Slash (قد يحتاج ظهورها لبعض الوقت).")
    except Exception as e:
        print("⚠️ فشل المزامنة العالمية:", e)

    # نعمل أيضًا مزامنة سريعة لسيرفرك التجريبي لتظهر الأوامر فورًا هناك
    try:
        synced_g = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ تمت مزامنة محلية للسيرفر التجريبي ({len(synced_g)} أمر).")
    except Exception as e:
        print("⚠️ لم أتمكن من مزامنة الأوامر للسيرفر التجريبي:", e)


@bot.tree.command(name="setwelcome", description="يرسل رسالة الترحيب", guild=discord.Object(id=GUILD_ID))
async def setwelcome(interaction: discord.Interaction):
    embed = discord.Embed(
        title="مرحبًا بك في Titabronsia...",
        description=(
            "عالم خيالي لا تصل إليه الأرجل، بل تهمس لك البوابة القديمة باسمه في لحظة شرود.\n"
            "هنا، تتلاشى حدود الواقع، وتنبض الأرض بقوانينها الخاصة...\n"
            "🔔 عند جاهزيتك، افتح البوابة عبر الزر أدناه، وانضم رسميًا إلى أعماق Titabronsia."
        ),
        color=discord.Color.purple()
    )
    await interaction.response.send_message(embed=embed, view=WelcomeView())


# ---------- وظائف المساعدة للنوم/الاستيقاظ ----------
async def _spam_loop(channel: discord.TextChannel, guild_id: int):
    """يرسل رسالة كل 20 ثانية حتى يتم إلغاء الحالة أو المهمة تُلغى"""
    try:
        while True:
            if guild_id not in guild_states:
                break
            try:
                await channel.send("اذهبوا للنوم")
            except Exception as e:
                print("⚠️ failed to send spam message:", e)
            await asyncio.sleep(20)
    except asyncio.CancelledError:
        return


async def _do_wake(guild_id: int, notify: bool = True):
    """استرجاع الصلاحيات وحذف قناة النوم"""
    state = guild_states.get(guild_id)
    if not state:
        return

    guild = bot.get_guild(guild_id)
    if not guild:
        # قد لا يكون في الكاش — نحاول إنهاء الحالة فقط
        try:
            # إلغاء المهمة إن كانت موجودة
            task = state.get("spam_task")
            if task and not task.done():
                task.cancel()
        except:
            pass
        guild_states.pop(guild_id, None)
        return

    # أوقف الـ spam task
    task = state.get("spam_task")
    if task and not task.done():
        task.cancel()

    # حذف قناة النوم
    try:
        ch = bot.get_channel(state.get("bedtime_channel_id"))
        if ch:
            await ch.delete(reason="End of bedtime")
    except Exception as e:
        print("⚠️ فشل حذف قناة النوم:", e)

    # إذا كنا في وضع fallback (role-based)، نستدعي إعادة الإظهار عبر @everyone
    if state.get("fallback_role_used"):
        # نجعل @everyone مرئيًا للقنوات
        for channel in guild.channels:
            try:
                await channel.set_permissions(guild.default_role, view_channel=True)
                await asyncio.sleep(0.02)
            except Exception as e:
                print("⚠️ فشل استعادة صلاحية @everyone في:", channel, e)

    else:
        # استرجاع الصلاحيات لكل عضو (التي خزناها)
        prev = state.get("prev_overwrites", {})
        for member_id, ch_map in prev.items():
            # نحاول أخذ العضو من الكاش أو fetch
            member = guild.get_member(member_id)
            if member is None:
                try:
                    member = await guild.fetch_member(member_id)
                except Exception:
                    continue
            for ch_id, prev_overwrite in ch_map.items():
                channel = guild.get_channel(ch_id)
                if not channel:
                    continue
                try:
                    if prev_overwrite is None:
                        # حذف أي overwrite إنشأناه
                        await channel.set_permissions(member, overwrite=None)
                    else:
                        # إعادة overwrite القديمة
                        await channel.set_permissions(member, overwrite=prev_overwrite)
                except Exception as e:
                    print(f"⚠️ فشل استرجاع صلاحيات {member} في {channel}: {e}")
                await asyncio.sleep(0.02)

    # أنهِ الحالة
    guild_states.pop(guild_id, None)

    # إذا أردنا الإشعار، نرسل رسالة في أول قناة نصية إن وجدت
    if notify:
        try:
            text_chs = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
            if text_chs:
                await text_chs[0].send("☀️ تم إلغاء وضع النوم — القنوات الآن مفتوحة.")
        except Exception:
            pass


# ---------- أوامر Slash: /sleep و /wake ----------
@bot.tree.command(name="sleep", description="وضع السيرفر في حالة نوم (إخفاء الرومات عن الأعضاء غير الأدمن)", guild=discord.Object(id=GUILD_ID))
async def sleep(interaction: discord.Interaction, hours: Optional[float] = None):
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild = interaction.guild
    invoker = interaction.user

    # صلاحية المشغل
    if not invoker.guild_permissions.administrator:
        await interaction.followup.send("❌ هذا الأمر مخصص للإدارة فقط.", ephemeral=True)
        return

    if guild.id in guild_states:
        await interaction.followup.send("⚠️ وضع النوم مفعل بالفعل في هذا السيرفر.", ephemeral=True)
        return

    # إنشاء قناة النوم أولاً
    try:
        bedtime_channel = await guild.create_text_channel("حان وقت النوم")
        # نجعلها مرئية للجميع لكن مقفلة للكتابة
        await bedtime_channel.set_permissions(guild.default_role, view_channel=True, send_messages=False)
    except Exception as e:
        await interaction.followup.send(f"❌ فشل إنشاء قناة النوم: {e}", ephemeral=True)
        return

    # نجلب كل الأعضاء من السيرفر (مطلوب Server Members Intent مفعل)
    try:
        members = [m async for m in guild.fetch_members(limit=None)]
    except Exception as e:
        # فشل في fetch -> نؤشر للمستخدم ونخرج
        await interaction.followup.send(
            "❌ فشل جلب الأعضاء (تأكد من تفعيل Server Members Intent في Developer Portal).", ephemeral=True
        )
        print("fetch_members failed:", e)
        return

    # قنوات التي سنعدل عليها (نستثني قناة النوم)
    channels_to_modify = [c for c in guild.channels if c.id != bedtime_channel.id]

    # أعضاء نطبّق عليهم التغيير (تجاهل البوتات والأدمنز)
    members_to_modify = [m for m in members if (not m.guild_permissions.administrator) and (not m.bot)]

    total_ops = len(members_to_modify) * len(channels_to_modify)
    # حد حماية لتفادي عمل ضخم قد يؤدي للـ Rate Limits
    MAX_OPS_SAFE = 1200

    state: dict = {"bedtime_channel_id": bedtime_channel.id, "created_at": datetime.datetime.utcnow().isoformat()}

    if total_ops > MAX_OPS_SAFE:
        # fallback: نعدل @everyone بدلاً من كل عضو واحدًا تلو الآخر
        state["fallback_role_used"] = True
        for ch in channels_to_modify:
            try:
                await ch.set_permissions(guild.default_role, view_channel=False)
            except Exception as e:
                print("⚠️ failed to set @everyone on", ch, e)
            await asyncio.sleep(0.02)

        # نجعل قناة النوم مرئية (تأكد)
        try:
            await bedtime_channel.set_permissions(guild.default_role, view_channel=True, send_messages=False)
        except:
            pass

        # ابدأ مهمة الإرسال الدوري
        spam_task = bot.loop.create_task(_spam_loop(bedtime_channel, guild.id))
        state["spam_task"] = spam_task
        guild_states[guild.id] = state

        msg = f"🌙 تم تفعيل وضع النوم (طريقة Role-based fallback لأن العمليات > {MAX_OPS_SAFE}). سيتم قفل قنوات السيرفر عن الجميع (عدا الأدمنز)."
        if hours:
            msg += f"\n⏰ سيعود السيرفر بعد {hours} ساعة تلقائيًا."
            bot.loop.create_task(_auto_wake_after(guild.id, hours, bedtime_channel.id))
        await interaction.followup.send(msg, ephemeral=True)
        return

    # وإلا: نطبّق التغييرات لكل عضو واحدًا تلو الآخر (نخزّن الـ overwrites القديمة)
    prev_overwrites: dict = {}  # member_id -> {channel_id -> PermissionOverwrite or None}
    try:
        for member in members_to_modify:
            prev_overwrites[member.id] = {}
            for ch in channels_to_modify:
                # نتحقق إذا كان هناك overwrite مخصص لهذا العضو داخل القناة
                existing = None
                try:
                    # channel.overwrites يُخزن كـ dict mapping (Role/Member) -> PermissionOverwrite
                    for target, overwrite in ch.overwrites.items():
                        # بعض المفاتيح قد تكون role أو member أو غيرها
                        try:
                            if isinstance(target, discord.Member) and target.id == member.id:
                                existing = overwrite
                                break
                        except Exception:
                            # fallback: تحقق من وجود id
                            if getattr(target, "id", None) == member.id:
                                existing = overwrite
                                break
                except Exception:
                    existing = None

                prev_overwrites[member.id][ch.id] = existing

                # ضع منع الرؤية لهذا العضو في هذه القناة
                try:
                    await ch.set_permissions(member, view_channel=False)
                except Exception as e:
                    print(f"⚠️ خطأ عند set_permissions لـ {member} في {ch}: {e}")
                # فاصل صغير لتقليل خطر الـ rate-limit
                await asyncio.sleep(0.02)

        # ابدأ مهمة الإرسال الدوري
        spam_task = bot.loop.create_task(_spam_loop(bedtime_channel, guild.id))
        state["prev_overwrites"] = prev_overwrites
        state["spam_task"] = spam_task
        guild_states[guild.id] = state

        msg = f"🌙 تم تفعيل وضع النوم — تم إخفاء القنوات عن {len(members_to_modify)} عضو/أعضاء (باستثناء الأدمنز)."
        if hours:
            msg += f"\n⏰ سيعود السيرفر بعد {hours} ساعة تلقائيًا."
            bot.loop.create_task(_auto_wake_after(guild.id, hours, bedtime_channel.id))

        await interaction.followup.send(msg, ephemeral=True)

    except Exception as e:
        # فشل عام: نعلن ونحاول التراجع
        print("❌ خطأ أثناء تطبيق وضع النوم:", e)
        # محاولة إلغاء المهمة واستعادة ما أمكن
        try:
            await _do_wake(guild.id, notify=False)
        except:
            pass
        await interaction.followup.send("❌ حدث خطأ أثناء تفعيل وضع النوم. حاول مجددًا أو راجع الصلاحيات.", ephemeral=True)


async def _auto_wake_after(guild_id: int, hours: float, bedtime_channel_id: int):
    """مهمة تستيقظ بعد ساعات معينة"""
    try:
        await asyncio.sleep(max(0.0, hours * 3600.0))
        await _do_wake(guild_id, notify=True)
    except Exception as e:
        print("⚠️ خطأ في auto_wake:", e)


@bot.tree.command(name="wake", description="إلغاء وضع النوم وإعادة القنوات لطبيعتها", guild=discord.Object(id=GUILD_ID))
async def wake(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild = interaction.guild
    invoker = interaction.user

    if not invoker.guild_permissions.administrator:
        await interaction.followup.send("❌ هذا الأمر مخصص للإدارة فقط.", ephemeral=True)
        return

    if guild.id not in guild_states:
        await interaction.followup.send("⚠️ وضع النوم غير مفعل في هذا السيرفر.", ephemeral=True)
        return

    # نفّذ الاستيقاظ (استعادة الصلاحيات)
    try:
        await _do_wake(guild.id, notify=True)
        await interaction.followup.send("🌞 تم إلغاء وضع النوم واستعادة الأذونات.", ephemeral=True)
    except Exception as e:
        print("❌ خطأ أثناء wake:", e)
        await interaction.followup.send("❌ فشل أثناء استعادة الصلاحيات. راجع السجلات.", ephemeral=True)


# ---- شغّل الويب ثم البوت ----
keep_alive()

try:
    bot.run(TOKEN)
except Exception as e:
    print("❌ فشل تشغيل البوت:", e)
    raise
