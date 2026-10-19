import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# লগিং চালু করা (Render-এর লগে এরর দেখার জন্য)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# এনভায়রনমেন্ট ভেরিয়েবল থেকে টোকেন নেওয়া
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
HF_TOKEN = os.environ["HF_TOKEN"]

# তোমার দেওয়া Hugging Face OpenAI ক্লায়েন্ট সেটআপ
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# হ্যালুসিনেশন বন্ধ করার জন্য কড়া সিস্টেম প্রম্পট
SYSTEM_PROMPT = """তুমি একজন অত্যন্ত নির্ভরযোগ্য এবং সত্যবাদী এআই অ্যাসিস্ট্যান্ট। 
তোমার প্রধান নিয়মাবলী:
১. কখনোই কোনো তথ্য অনুমান করে বা বানিয়ে বলবে না (No Hallucination)।
২. কোনো প্রশ্নের সঠিক বা নিশ্চিত উত্তর জানা না থাকলে বা রিয়েল-টাইম ইন্টারনেটের তথ্যের প্রয়োজন হলে সরাসরি বলবে: 'আমার কাছে এই মুহূর্তে এর সঠিক বা সাম্প্রতিক তথ্য নেই।'
৩. সবসময় স্পষ্ট, সঠিক এবং স্বাভাবিক বাংলায় উত্তর দেবে।"""

# ইউজারের চ্যাট হিস্ট্রি মনে রাখার ডিকশনারি (যাতে ChatGPT-এর মতো কথোপকথন চালানো যায়)
user_histories = {}

# /start কমান্ড দিলে যা বলবে
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text(
        "হ্যালো! আমি তোমার এআই চ্যাটবট। আমাকে যেকোনো প্রশ্ন করতে পারো বা ছবি পাঠাতে পারো।\n"
        "(চ্যাট রিসেট করতে /clear লিখবে)"
    )

# /clear কমান্ড দিলে আগের কথা ভুলে নতুন করে শুরু করবে
async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text("চ্যাট হিস্ট্রি মুছে ফেলা হয়েছে! নতুন করে কথা শুরু করো।")

# সাধারণ টেক্সট মেসেজ হ্যান্ডেল করা
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # ইউজারের মেসেজ হিস্ট্রিতে যোগ করা
    user_histories[user_id].append({
        "role": "user",
        "content": [{"type": "text", "text": user_text}]
    })

    # মেমরি হালকা রাখতে শেষ ১০টি মেসেজ রাখা হচ্ছে
    if len(user_histories[user_id]) > 11:
        user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-10:]

    # টেলিগ্রামে "Typing..." দেখাবে
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4.1-Flash:novita",
            messages=user_histories[user_id],
            temperature=0.2,  # ০.২ দেওয়ার কারণে মডেল ভুলভাল বানিয়ে কথা বলবে না
        )
        
        bot_reply = completion.choices[0].message.content

        # বটের উত্তরও হিস্ট্রিতে সেভ করা হচ্ছে
        user_histories[user_id].append({
            "role": "assistant",
            "content": bot_reply
        })

        await update.message.reply_text(bot_reply)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("দুঃখিত, উত্তর তৈরি করতে একটু সমস্যা হয়েছে। আবার চেষ্টা করো।")

# ছবি (Image) পাঠালে তা হ্যান্ডেল করা (তোমার দেওয়া কোডের ফরম্যাট অনুযায়ী)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_caption = update.message.caption or "এই ছবিটি সম্পর্কে বিস্তারিত বলো।"
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # টেলিগ্রাম থেকে ছবির ডিরেক্ট লিংক বের করা
        photo_file = await update.message.photo[-1].get_file()
        image_url = photo_file.file_path

        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4.1-Flash:novita",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_caption},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            temperature=0.2,
        )

        bot_reply = completion.choices[0].message.content
        await update.message.reply_text(bot_reply)

    except Exception as e:
        logging.error(f"Photo Error: {e}")
        await update.message.reply_text("ছবিটি বিশ্লেষণ করতে সমস্যা হয়েছে।")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # কমান্ড এবং মেসেজ হ্যান্ডলার যুক্ত করা
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("বট সফলভাবে চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
