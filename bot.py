#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
بوت اختبارات أساسيات شبكات الحاسب
يحتوي على نظام كامل للاختبارات مع إحصائيات مفصلة
مع ميزة الانتقال التلقائي للسؤال التالي
مع Keep-Alive للعمل 24/7 على Render
"""

import json
import logging
import random
import os
import asyncio
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# استيراد Flask للـ Keep-Alive
from flask import Flask
from threading import Thread

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إعداد Flask للـ Keep-Alive
app = Flask(__name__)

@app.route('/')
def home():
    """صفحة رئيسية بسيطة للتحقق من عمل البوت"""
    return """
    <html>
        <head>
            <meta charset="UTF-8">
            <title>Telegram Quiz Bot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                }
                h1 { font-size: 2.5em; margin-bottom: 20px; }
                p { font-size: 1.2em; }
                .status { color: #4ade80; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 بوت اختبارات شبكات الحاسب</h1>
                <p class="status">✅ البوت يعمل بنجاح!</p>
                <p>📊 عدد الأسئلة: 34 سؤال</p>
                <p>🔗 ابحث عن البوت في Telegram: <strong>@cs_networks_bot</strong></p>
                <hr style="margin: 30px 0; border: 1px solid rgba(255,255,255,0.3);">
                <p style="font-size: 0.9em;">Bot is running on Render 🚀</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """نقطة فحص صحة البوت"""
    return {"status": "ok", "bot": "running"}, 200

def run_flask():
    """تشغيل Flask في thread منفصل"""
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# تحميل الأسئلة من ملف JSON
def load_questions():
    """تحميل الأسئلة من ملف JSON"""
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("ملف questions.json غير موجود!")
        return []
    except json.JSONDecodeError:
        logger.error("خطأ في قراءة ملف questions.json!")
        return []

# تحميل الأسئلة
QUESTIONS = load_questions()
TOTAL_QUESTIONS = len(QUESTIONS)

# تخزين بيانات المستخدمين
user_data: Dict[int, Dict] = {}

def get_user_data(user_id: int) -> Dict:
    """الحصول على بيانات المستخدم أو إنشاؤها"""
    if user_id not in user_data:
        user_data[user_id] = {
            'score': 0,
            'total_answered': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'asked_questions': [],
            'current_question': None
        }
    return user_data[user_id]

def get_final_results_text(user_id: int) -> str:
    """الحصول على نص النتيجة النهائية"""
    data = get_user_data(user_id)
    
    percentage = (data['score'] / data['total_answered'] * 100) if data['total_answered'] > 0 else 0
    
    # تحديد التقييم
    if percentage >= 90:
        rating = "ممتاز 🌟"
    elif percentage >= 80:
        rating = "جيد جداً 👍"
    elif percentage >= 70:
        rating = "جيد ✓"
    elif percentage >= 60:
        rating = "مقبول"
    else:
        rating = "يحتاج تحسين"
    
    results = f"""📊 **الإحصائيات الكاملة:**

✅ إجابات صحيحة: {data['correct_answers']}
❌ إجابات خاطئة: {data['wrong_answers']}
📝 إجمالي الأسئلة: {data['total_answered']} من {TOTAL_QUESTIONS}

🎯 النسبة المئوية: {percentage:.1f}%
⭐ التقييم: {rating}
"""
    return results

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # إعادة تعيين بيانات المستخدم
    if user_id in user_data:
        user_data[user_id] = {
            'score': 0,
            'total_answered': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'asked_questions': [],
            'current_question': None
        }
    
    welcome_text = f"""👋 مرحباً {user_name}!

🎓 **بوت اختبارات أساسيات شبكات الحاسب**

📊 **عدد الأسئلة:** {TOTAL_QUESTIONS} سؤال

📚 **الأوامر المتاحة:**
/quiz - بدء الاختبار
/score - عرض نتيجتك
/stats - عرض إحصائيات مفصلة
/reset - البدء من جديد
/help - عرض المساعدة

✨ اضغط على /quiz لبدء الاختبار!
"""
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help"""
    help_text = """📖 **كيفية استخدام البوت:**

1️⃣ اضغط على /quiz لبدء الاختبار
2️⃣ سيتم عرض سؤال مع خيارات متعددة
3️⃣ اختر الإجابة الصحيحة من الأزرار
4️⃣ سيتم إخبارك فوراً إذا كانت إجابتك صحيحة أو خاطئة
5️⃣ **سيظهر السؤال التالي تلقائياً** بعد 3 ثوانٍ
6️⃣ بعد الإجابة على جميع الأسئلة، ستظهر النتيجة النهائية تلقائياً

**ملاحظات:**
• كل سؤال يظهر مرة واحدة فقط
• بعد الانتهاء من جميع الأسئلة، يمكنك البدء من جديد
• استخدم /reset لإعادة تعيين النتائج والبدء من جديد

حظاً موفقاً! 🍀"""
    
    await update.message.reply_text(help_text)

async def send_next_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """إرسال السؤال التالي"""
    data = get_user_data(user_id)
    
    # التحقق من وجود أسئلة
    if not QUESTIONS:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ عذراً، لا توجد أسئلة متاحة حالياً."
        )
        return
    
    # التحقق من إنهاء جميع الأسئلة
    if len(data['asked_questions']) >= TOTAL_QUESTIONS:
        results_text = "🎊 **النتيجة النهائية**\n\n"
        results_text += get_final_results_text(user_id)
        results_text += "\n\nاستخدم /reset للبدء من جديد"
        await context.bot.send_message(chat_id=chat_id, text=results_text)
        return
    
    # اختيار سؤال عشوائي لم يتم طرحه
    available_questions = [
        i for i in range(TOTAL_QUESTIONS)
        if i not in data['asked_questions']
    ]
    
    if not available_questions:
        results_text = "🎊 **النتيجة النهائية**\n\n"
        results_text += get_final_results_text(user_id)
        results_text += "\n\nاستخدم /reset للبدء من جديد"
        await context.bot.send_message(chat_id=chat_id, text=results_text)
        return
    
    question_index = random.choice(available_questions)
    question_data = QUESTIONS[question_index]
    
    # حفظ السؤال الحالي
    data['current_question'] = question_index
    
    # إنشاء أزرار الخيارات
    keyboard = []
    for i, option in enumerate(question_data['options']):
        keyboard.append([
            InlineKeyboardButton(
                f"{chr(65+i)}. {option}",
                callback_data=f"answer_{question_index}_{i}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # عرض السؤال مع المعلومات
    remaining = TOTAL_QUESTIONS - len(data['asked_questions'])
    question_text = f"""❓ **السؤال {len(data['asked_questions']) + 1} من {TOTAL_QUESTIONS}**

{question_data['question']}

📊 **الأسئلة المتبقية:** {remaining - 1}
"""
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=question_text,
        reply_markup=reply_markup
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /quiz - عرض سؤال جديد"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    await send_next_question(chat_id, context, user_id)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الإجابات"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    data = get_user_data(user_id)
    
    # تحليل البيانات
    try:
        _, question_index, selected_option = query.data.split('_')
        question_index = int(question_index)
        selected_option = int(selected_option)
    except (ValueError, IndexError):
        await query.edit_message_text("❌ خطأ في معالجة الإجابة.")
        return
    
    # التحقق من السؤال
    if question_index >= len(QUESTIONS):
        await query.edit_message_text("❌ سؤال غير صالح.")
        return
    
    question_data = QUESTIONS[question_index]
    correct_answer = question_data['correct']
    
    # تحديث الإحصائيات
    data['asked_questions'].append(question_index)
    data['total_answered'] += 1
    
    # التحقق من الإجابة
    is_correct = (selected_option == correct_answer)
    
    if is_correct:
        data['score'] += 1
        data['correct_answers'] += 1
        result_emoji = "✅"
        result_text = "**إجابة صحيحة!** 🎉"
    else:
        data['wrong_answers'] += 1
        result_emoji = "❌"
        result_text = "**إجابة خاطئة!**"
        correct_option_text = question_data['options'][correct_answer]
        result_text += f"\n\n✅ الإجابة الصحيحة: {correct_option_text}"
    
    # حساب النسبة المئوية
    percentage = (data['score'] / data['total_answered']) * 100
    
    response = f"""{result_emoji} {result_text}

💡 **الشرح:**
{question_data['explanation']}

📊 **نتيجتك الحالية:**
{data['score']} / {data['total_answered']} ({percentage:.0f}%)

"""
    
    # التحقق من إنهاء جميع الأسئلة
    if len(data['asked_questions']) >= TOTAL_QUESTIONS:
        response += "\n🎊 **تهانينا! أكملت جميع الأسئلة!**\n\n"
        response += get_final_results_text(user_id)
        response += "\n\nاستخدم /reset للبدء من جديد"
        await query.edit_message_text(response)
    else:
        response += "⏳ السؤال التالي سيظهر خلال 3 ثوانٍ..."
        await query.edit_message_text(response)
        
        # إرسال السؤال التالي بعد 3 ثوانٍ
        await asyncio.sleep(3)
        await send_next_question(chat_id, context, user_id)

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /score - عرض النتيجة الحالية"""
    user_id = update.effective_user.id
    data = get_user_data(user_id)
    
    if data['total_answered'] == 0:
        await update.message.reply_text("📊 لم تجب على أي سؤال بعد!\n\nاستخدم /quiz لبدء الاختبار.")
        return
    
    percentage = (data['score'] / data['total_answered']) * 100
    
    score_text = f"""📊 **نتيجتك الحالية:**

✅ إجابات صحيحة: {data['correct_answers']}
❌ إجابات خاطئة: {data['wrong_answers']}
📝 إجمالي الأسئلة: {data['total_answered']} من {TOTAL_QUESTIONS}

🎯 النسبة المئوية: {percentage:.1f}%

📈 الأسئلة المتبقية: {TOTAL_QUESTIONS - len(data['asked_questions'])}
"""
    
    await update.message.reply_text(score_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /stats - عرض إحصائيات مفصلة"""
    user_id = update.effective_user.id
    data = get_user_data(user_id)
    
    if data['total_answered'] == 0:
        await update.message.reply_text("📊 لا توجد إحصائيات بعد!\n\nاستخدم /quiz لبدء الاختبار.")
        return
    
    stats_text = get_final_results_text(user_id)
    stats_text += f"\n📈 **التقدم:** {len(data['asked_questions'])} / {TOTAL_QUESTIONS} ({len(data['asked_questions'])/TOTAL_QUESTIONS*100:.1f}%)"
    
    await update.message.reply_text(stats_text)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /reset - إعادة تعيين النتائج"""
    user_id = update.effective_user.id
    
    # إعادة تعيين البيانات
    user_data[user_id] = {
        'score': 0,
        'total_answered': 0,
        'correct_answers': 0,
        'wrong_answers': 0,
        'asked_questions': [],
        'current_question': None
    }
    
    await update.message.reply_text(
        "🔄 تم إعادة تعيين النتائج بنجاح!\n\n"
        "استخدم /quiz لبدء الاختبار من جديد."
    )

def main():
    """تشغيل البوت"""
    # التوكن من متغيرات البيئة
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    
    if not TOKEN:
        logger.error("⚠️ يرجى تعيين متغير البيئة TELEGRAM_TOKEN!")
        return
    
    # تشغيل Flask في thread منفصل للـ Keep-Alive
    logger.info("🌐 تشغيل Flask server للـ Keep-Alive...")
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("score", score))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))
    
    # تشغيل البوت
    logger.info(f"🤖 البوت يعمل الآن على Render... (عدد الأسئلة: {TOTAL_QUESTIONS})")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
