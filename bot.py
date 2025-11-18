#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تلقرام للاختبارات - أساسيات شبكات الحاسب
يقدم اختبارات تفاعلية مع نظام تتبع النقاط
"""
import os
TOKEN = os.environ.get("TELEGRAM_TOKEN")

import json
import random
import logging
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)

# إعداد نظام السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حالات المحادثة
ANSWERING = 1

# تحميل الأسئلة من ملف JSON
def load_questions() -> List[Dict]:
    """تحميل الأسئلة من ملف JSON"""
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['questions']
    except FileNotFoundError:
        logger.error("ملف questions.json غير موجود!")
        return []
    except json.JSONDecodeError:
        logger.error("خطأ في قراءة ملف JSON!")
        return []

# تحميل الأسئلة عند بدء البوت
QUESTIONS = load_questions()

# تخزين بيانات المستخدمين
user_data_store: Dict[int, Dict] = {}

def get_user_data(user_id: int) -> Dict:
    """الحصول على بيانات المستخدم أو إنشاء بيانات جديدة"""
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            'score': 0,
            'total_questions': 0,
            'current_question': None,
            'answered_questions': []
        }
    return user_data_store[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start"""
    user = update.effective_user
    user_id = user.id
    
    # إعادة تعيين بيانات المستخدم
    user_data_store[user_id] = {
        'score': 0,
        'total_questions': 0,
        'current_question': None,
        'answered_questions': []
    }
    
    welcome_message = f"""
👋 مرحباً {user.first_name}!

🎓 **بوت اختبارات أساسيات شبكات الحاسب**

هذا البوت يساعدك على اختبار معلوماتك في مجال شبكات الحاسب من خلال أسئلة اختيار من متعدد.

📚 **الأوامر المتاحة:**
/start - بدء جديد وإعادة تعيين النقاط
/quiz - بدء الاختبار
/score - عرض نتيجتك الحالية
/stats - عرض إحصائيات مفصلة
/help - عرض المساعدة

✨ اضغط على /quiz لبدء الاختبار!
"""
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /help"""
    help_text = """
📖 **كيفية استخدام البوت:**

1️⃣ اضغط على /quiz لبدء الاختبار
2️⃣ سيتم عرض سؤال مع خيارات متعددة
3️⃣ اختر الإجابة الصحيحة من الأزرار
4️⃣ سيتم إخبارك فوراً إذا كانت إجابتك صحيحة أم خاطئة
5️⃣ يمكنك متابعة الإجابة على المزيد من الأسئلة
6️⃣ استخدم /score لمعرفة نتيجتك في أي وقت

💡 **نصائح:**
• كل سؤال له 4 خيارات، واحد منها فقط صحيح
• يتم اختيار الأسئلة بشكل عشوائي
• يمكنك إعادة البدء في أي وقت باستخدام /start

حظاً موفقاً! 🍀
"""
    await update.message.reply_text(help_text)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء سؤال جديد"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    if not QUESTIONS:
        await update.message.reply_text("⚠️ عذراً، لا توجد أسئلة متاحة حالياً.")
        return ConversationHandler.END
    
    # اختيار سؤال عشوائي
    question = random.choice(QUESTIONS)
    user_data['current_question'] = question
    
    # إنشاء أزرار الخيارات
    keyboard = []
    for i, option in enumerate(question['options']):
        keyboard.append([InlineKeyboardButton(
            f"{chr(65 + i)}) {option}",
            callback_data=f"answer_{i}"
        )])
    
    # إضافة زر الإلغاء
    keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    question_text = f"""
❓ **السؤال رقم {user_data['total_questions'] + 1}:**

{question['question']}

اختر الإجابة الصحيحة:
"""
    
    await update.message.reply_text(question_text, reply_markup=reply_markup)
    return ANSWERING

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """معالجة إجابة المستخدم"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    if query.data == "cancel":
        await query.edit_message_text("❌ تم إلغاء السؤال.")
        return ConversationHandler.END
    
    # استخراج رقم الإجابة
    answer_index = int(query.data.split('_')[1])
    current_question = user_data['current_question']
    
    if not current_question:
        await query.edit_message_text("⚠️ حدث خطأ، الرجاء المحاولة مرة أخرى.")
        return ConversationHandler.END
    
    # تحديث الإحصائيات
    user_data['total_questions'] += 1
    user_data['answered_questions'].append(current_question['id'])
    
    # التحقق من الإجابة
    is_correct = answer_index == current_question['correct_answer']
    
    if is_correct:
        user_data['score'] += 1
        result_emoji = "✅"
        result_text = "**إجابة صحيحة!** 🎉"
    else:
        result_emoji = "❌"
        correct_option = current_question['options'][current_question['correct_answer']]
        result_text = f"**إجابة خاطئة!**\n\n✅ الإجابة الصحيحة: {correct_option}"
    
    # عرض النتيجة مع الشرح
    response = f"""
{result_emoji} {result_text}

💡 **الشرح:**
{current_question['explanation']}

📊 **نتيجتك الحالية:**
{user_data['score']} / {user_data['total_questions']} ({int(user_data['score'] / user_data['total_questions'] * 100)}%)

استخدم /quiz للسؤال التالي
استخدم /score لعرض الإحصائيات
"""
    
    await query.edit_message_text(response)
    return ConversationHandler.END

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض النتيجة الحالية"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    if user_data['total_questions'] == 0:
        await update.message.reply_text(
            "📊 لم تجب على أي سؤال بعد!\n\n"
            "استخدم /quiz لبدء الاختبار."
        )
        return
    
    percentage = int(user_data['score'] / user_data['total_questions'] * 100)
    
    # تحديد التقييم بناءً على النسبة
    if percentage >= 90:
        grade = "ممتاز 🌟"
    elif percentage >= 80:
        grade = "جيد جداً 👍"
    elif percentage >= 70:
        grade = "جيد ✨"
    elif percentage >= 60:
        grade = "مقبول 📚"
    else:
        grade = "يحتاج تحسين 💪"
    
    score_text = f"""
📊 **نتيجتك الحالية:**

✅ الإجابات الصحيحة: {user_data['score']}
❌ الإجابات الخاطئة: {user_data['total_questions'] - user_data['score']}
📝 إجمالي الأسئلة: {user_data['total_questions']}
📈 النسبة المئوية: {percentage}%

🏆 التقييم: {grade}

استخدم /quiz لمواصلة الاختبار
استخدم /start لإعادة البدء من الصفر
"""
    
    await update.message.reply_text(score_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات مفصلة"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    if user_data['total_questions'] == 0:
        await update.message.reply_text(
            "📊 لا توجد إحصائيات بعد!\n\n"
            "استخدم /quiz لبدء الاختبار."
        )
        return
    
    percentage = int(user_data['score'] / user_data['total_questions'] * 100)
    wrong_answers = user_data['total_questions'] - user_data['score']
    
    stats_text = f"""
📈 **إحصائيات مفصلة:**

👤 **المستخدم:** {update.effective_user.first_name}

📊 **الأداء العام:**
• الإجابات الصحيحة: {user_data['score']} ✅
• الإجابات الخاطئة: {wrong_answers} ❌
• إجمالي الأسئلة: {user_data['total_questions']} 📝
• نسبة النجاح: {percentage}% 📈

📚 **معلومات إضافية:**
• عدد الأسئلة المتاحة: {len(QUESTIONS)}
• الأسئلة المجاب عليها: {len(user_data['answered_questions'])}

💡 استمر في التدريب لتحسين نتيجتك!
"""
    
    await update.message.reply_text(stats_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """إلغاء المحادثة"""
    await update.message.reply_text("تم الإلغاء. استخدم /quiz لبدء اختبار جديد.")
    return ConversationHandler.END

def main() -> None:
    """تشغيل البوت"""
    # ضع توكن البوت الخاص بك هنا
    "TOKEN = "1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

    
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("score", score))
    application.add_handler(CommandHandler("stats", stats))
    
    # معالج المحادثة للاختبار
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("quiz", quiz)],
        states={
            ANSWERING: [CallbackQueryHandler(answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # بدء البوت
    logger.info("🤖 البوت يعمل الآن...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
