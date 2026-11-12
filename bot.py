import os
import base64
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ১. এনভায়রনমেন্ট ভেরিয়েবল থেকে টোকেন নেওয়া (অথবা এখানে সরাসরি তোমার BotFather-এর টোকেন বসাতে পারো)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# ২. রেন্ডারে ডিপ্লয় করা তোমার লাইভ এপিআই এন্ডপয়েন্ট
API_ENDPOINT = "https://newsvibe-ai.onrender.com/generate-news"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "নমস্কার! আমি আপনার এআই সংবাদ বিশ্লেষক ও অডিও ভয়েস বট।\n\n"
        "কোনো খবরের গভীর বিশ্লেষণ ও গম্ভীর গলার অডিও শুনতে এই কমান্ড দিন:\n"
        "👉 `/news [আপনার বিষয় যেমন: পশ্চিমবঙ্গের শিক্ষা ব্যবস্থা]`"
    )
    await update.message.reply_text(welcome_text)

async def get_news_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("দয়া করে বিষয়ের নাম দিন। যেমন: `/news পশ্চিমবঙ্গের শিক্ষা ব্যবস্থা`")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 '{query}' বিষয়ে তথ্য সংগ্রহ করে গভীর বিশ্লেষণ ও গম্ভীর অডিও তৈরি হচ্ছে, একটু অপেক্ষা করুন...")

    try:
        # রেন্ডার এপিআই-এ POST রিকোয়েস্ট পাঠানো
        response = requests.post(API_ENDPOINT, json={"query": query, "max_items": 5}, timeout=60)
        
        if response.status_code != 200:
            await update.message.reply_text("দুঃখিত, সার্ভার থেকে তথ্য আনতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
            return

        data = response.json()
        headline = data.get("headline", "")
        summary = data.get("summary", "")
        audio_base64 = data.get("audio_base64", "")

        # ১. টেলিগ্রামে বিশ্লেষণাত্মক টেক্সট পাঠানো
        message_text = f"📰 *{headline}*\n\n{summary}"
        await update.message.reply_text(message_text, parse_mode="Markdown")

        # ২. Base64 থেকে অডিও ফাইল ডিকোড করে টেলিগ্রামে ভয়েস বা অডিও ফাইল পাঠানো
        if audio_base64:
            audio_bytes = base64.b64decode(audio_base64)
            audio_filename = f"news_overview_{update.effective_chat.id}.mp3"
            
            with open(audio_filename, "wb") as f:
                f.write(audio_bytes)

            with open(audio_filename, "rb") as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=headline,
                    performer="Newsvibe AI",
                    caption="🎙️ গভীর বিশ্লেষণাত্মক অডিও ওভারভিউ (গম্ভীর পুরুষ কণ্ঠ)"
                )
            
            # লোকাল ফাইল ক্লিন করা
            if os.path.exists(audio_filename):
                os.remove(audio_filename)

    except Exception as e:
        await update.message.reply_text(f"ত্রুটি ঘটেছে: {str(e)}")

def main():
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("⚠️ সতর্কতা: দয়া করে আপনার সঠিক TELEGRAM_BOT_TOKEN সেট করুন!")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", get_news_overview))

    print("টেলিগ্রাম বট সফলভাবে চালু হয়েছে এবং রিকোয়েস্টের জন্য অপেক্ষা করছে...")
    application.run_polling()

if __name__ == "__main__":
    main()
