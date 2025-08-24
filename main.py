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
