
# ১. প্রয়োজনীয় লাইব্রেরি ইনস্টল করা
!pip install python-telegram-bot google-genai

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from google import genai

# ২. আপনার API কি এবং টোকেন এখানে বসান
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# Gemini ক্লায়েন্ট সেটআপ
client = genai.Client(api_key=GEMINI_API_KEY)

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ইউজারকে প্রাথমিক মেসেজ পাঠানো
    await update.message.reply_text("🤖 আপনার প্রজেক্টটি Gemini API এর মাধ্যমে ব্যাকএন্ডে স্টার্ট হচ্ছে... অনুগ্রহ করে অপেক্ষা করুন।")
    
    try:
        # Gemini মডেল কল করা (gemini-2.5-flash)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='টেলিগ্রাম বোটের জন্য একটি শুভেচ্ছা বার্তা তৈরি করো এবং বলো যে প্রজেক্টটি সফলভাবে ব্যাকএন্ডে চালু হয়েছে।'
        )
        
        # আউটপুট ফেরত পাঠানো
        await update.message.reply_text(f"✅ প্রজেক্ট সফলভাবে রান হয়েছে!\n\n{response.text}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ দুঃখিত, কোনো একটি সমস্যা হয়েছে: {str(e)}")

# ৩. বোট রান করার মূল ফাংশন
async def main():
    # অ্যাপ্লিকেশন তৈরি
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # কমান্ড হ্যান্ডলার যুক্ত করা
    application.add_handler(CommandHandler("start", start))
    
    # Colab-এর জন্য স্পেশাল সেটআপ (ইনিশিয়ালাইজ ও স্টার্ট)
    await application.initialize()
    await application.start()
    
    print("🤖 বোটটি সফলভাবে চালু হয়েছে! আপনার টেলিগ্রাম অ্যাপে গিয়ে /start চাপুন।")
    print("🔴 বোটটি বন্ধ করতে Colab সেলের Stop (■) বাটনে ক্লিক করুন।")
    
    # পোলিং শুরু করা
    await application.updater.start_polling()
    
    # বোট সচল রাখার জন্য লুপ
    while True:
        await asyncio.sleep(1)

# ৪. Colab-এর ইভেন্ট লুপে রান করা
if __name__ == '__main__':
    # Colab-এ অলরেডি ইভেন্ট লুপ চলতে থাকে, তাই সরাসরি await বা nest_asyncio ছাড়া এভাবে রান করতে হবে
    try:
        asyncio.ensure_future(main())
    except Exception as e:
        print(f"Error: {e}")
        
