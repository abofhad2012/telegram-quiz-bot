#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تلقرام للاختبارات - أساسيات شبكات الحاسب
"""

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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ANSWERING = 1

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

QUESTIONS = load_questions()
TOTAL_QUESTIONS = len(QUESTIONS)
user_data_store: Dict[int, Dict] = {}

def get_user_data(user_id: int) -> Dict:
    """الحصول على بيانات المستخدم"""
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            'score': 0,
            'total_questions': 0,
            'current_question': None,
            'answered_questions': [],
            'remaining_questions': list(range(len(QUESTIONS)))
        }
    return user_data_store[user_id]

def reset_user_quiz(user_id: int):
    """إعادة تعيين الاختبار للمستخدم"""
    if user_id in user_data_store:
        user_data_store[user_id]['remaining_questions'] = list(range(len(QUESTIONS)))
        random.shuffle(user_data_store[user_id]['remaining_questions'])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /start"""
    user = update.effective_user
    user_id = user.id
    
    user_data_store[user_id] = {
        'score': 0,
        'total_questions': 0,
        'current_question': None,
        'answered_questions': [],
        'remaining_questions': list(range(len(QUESTIONS)))
    }
    random.shuffle(user_data_store[user_id]['remaining_questions'])
    
    welcome_message = f"""
👋 مرحباً {user.first_name}!

🎓 **بوت اختبارات أساسيات شبكات الحاسب**

📊 **عدد الأسئلة:** {TOTAL_QUESTIONS} سؤال

📚 **الأوامر المتاحة:**
/quiz - بدء الاختبار
/score - عرض نتيجتك
/stats - عرض إحصائيات مفصلة
/help - عرض المساعدة

✨ اضغط على /quiz لبدء الاختبار!
"""
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /help"""
    help_text = f"""
📖 **كيفية استخدام البوت:**

1️⃣ اضغط على /quiz لبدء الاختبار
2️⃣ سيتم عرض سؤال مع خيارات متعددة
3️⃣ اختر الإجابة الصحيحة من الأزرار
4️⃣ سيتم إخبارك فوراً إذا كانت إجابتك صحيحة
5️⃣ بعد الإجابة على جميع الأسئلة ({TOTAL_QUESTIONS} سؤال)، سيتم عرض النتيجة النهائية تلقائياً
6️⃣ يمكنك إعادة الاختبار من البداية بعد الانتهاء

حظاً موفقاً! 🍀
"""
    await update.message.reply_text(help_text)

async def show_final_results(update: Update, user_data: Dict, user_name: str) -> None:
    """عرض النتيجة النهائية"""
    percentage = int(user_data['score'] / user_data['total_questions'] * 100)
    wrong_answers = user_data['total_questions'] - user_data['score']
    
    if percentage >= 90:
        grade = "ممتاز 🌟"
        emoji = "🏆"
    elif percentage >= 80:
        grade = "جيد جداً 👍"
        emoji = "🎉"
    elif percentage >= 70:
        grade = "جيد ✨"
        emoji = "👏"
    elif percentage >= 60:
        grade = "مقبول 📚"
        emoji = "📖"
    else:
        grade = "يحتاج تحسين 💪"
        emoji = "📝"
    
    final_message = f"""
{emoji} **النتيجة النهائية** {emoji}

👤 **المستخدم:** {user_name}

📊 **الأداء:**
✅ الإجابات الصحيحة: {user_data['score']}
❌ الإجابات الخاطئة: {wrong_answers}
📝 إجمالي الأسئلة: {user_data['total_questions']} / {TOTAL_QUESTIONS}
📈 النسبة المئوية: {percentage}%

🏆 **التقييم:** {grade}

━━━━━━━━━━━━━━━━━━━━

🔄 تم إعادة تعيين الأسئلة!
يمكنك البدء من جديد باستخدام /quiz

أو استخدم /start لإعادة تعيين النقاط
"""
    
    await update.message.reply_text(final_message)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """بدء سؤال جديد"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    if not QUESTIONS:
        await update.message.reply_text("⚠️ عذراً، لا توجد أسئلة متاحة حالياً.")
        return ConversationHandler.END
    
    # التحقق من انتهاء جميع الأسئلة
    if not user_data['remaining_questions']:
        # عرض النتيجة النهائية
        await show_final_results(update, user_data, update.effective_user.first_name)
        # إعادة تعيين الأسئلة
        reset_user_quiz(user_id)
        return ConversationHandler.END
    
    # اختيار سؤال عشوائي من الأسئلة المتبقية
    question_index = user_data['remaining_questions'].pop(0)
    question = QUESTIONS[question_index]
    user_data['current_question'] = question
    
    keyboard = []
    for i, option in enumerate(question['options']):
        keyboard.append([InlineKeyboardButton(
            f"{chr(65 + i)}) {option}",
            callback_data=f"answer_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    answered = user_data['total_questions']
    remaining = len(user_data['remaining_questions']) + 1  # +1 للسؤال الحالي
    
    question_text = f"""
❓ **السؤال رقم {answered + 1} من {TOTAL_QUESTIONS}**

📊 **الأسئلة المتبقية:** {remaining - 1}

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
    
    answer_index = int(query.data.split('_')[1])
    current_question = user_data['current_question']
    
    if not current_question:
        await query.edit_message_text("⚠️ حدث خطأ، الرجاء المحاولة مرة أخرى.")
        return ConversationHandler.END
    
    user_data['total_questions'] += 1
    user_data['answered_questions'].append(current_question['id'])
    
    is_correct = answer_index == current_question['correct_answer']
    
    if is_correct:
        user_data['score'] += 1
        result_emoji = "✅"
        result_text = "**إجابة صحيحة!** 🎉"
    else:
        result_emoji = "❌"
        correct_option = current_question['options'][current_question['correct_answer']]
        result_text = f"**إجابة خاطئة!**\n\n✅ الإجابة الصحيحة: {correct_option}"
    
    remaining = len(user_data['remaining_questions'])
    
    if remaining > 0:
        next_instruction = f"\n\n📝 **الأسئلة المتبقية:** {remaining}\nاستخدم /quiz للسؤال التالي"
    else:
        next_instruction = "\n\n🎊 **انتهيت من جميع الأسئلة!**\nاستخدم /quiz لعرض النتيجة النهائية"
    
    response = f"""
{result_emoji} {result_text}

💡 **الشرح:**
{current_question['explanation']}

📊 **نتيجتك الحالية:**
{user_data['score']} / {user_data['total_questions']} ({int(user_data['score'] / user_data['total_questions'] * 100)}%)
{next_instruction}
"""
    
    await query.edit_message_text(response)
    return ConversationHandler.END

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض النتيجة الحالية"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    if user_data['total_questions'] == 0:
        await update.message.reply_text(
            f"📊 لم تجب على أي سؤال بعد!\n\n"
            f"📚 عدد الأسئلة المتاحة: {TOTAL_QUESTIONS}\n\n"
            f"استخدم /quiz لبدء الاختبار."
        )
        return
    
    percentage = int(user_data['score'] / user_data['total_questions'] * 100)
    remaining = len(user_data['remaining_questions'])
    
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
📝 الأسئلة المجاب عليها: {user_data['total_questions']} / {TOTAL_QUESTIONS}
📈 النسبة المئوية: {percentage}%
📚 الأسئلة المتبقية: {remaining}

🏆 التقييم: {grade}
"""
    
    await update.message.reply_text(score_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض إحصائيات مفصلة"""
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    
    if user_data['total_questions'] == 0:
        await update.message.reply_text(
            f"📊 لا توجد إحصائيات بعد!\n\n"
            f"📚 عدد الأسئلة المتاحة: {TOTAL_QUESTIONS}\n\n"
            f"استخدم /quiz لبدء الاختبار."
        )
        return
    
    percentage = int(user_data['score'] / user_data['total_questions'] * 100)
    wrong_answers = user_data['total_questions'] - user_data['score']
    remaining = len(user_data['remaining_questions'])
    progress = int((user_data['total_questions'] / TOTAL_QUESTIONS) * 100)
    
    stats_text = f"""
📈 **إحصائيات مفصلة:**

👤 **المستخدم:** {update.effective_user.first_name}

📊 **الأداء العام:**
• الإجابات الصحيحة: {user_data['score']} ✅
• الإجابات الخاطئة: {wrong_answers} ❌
• الأسئلة المجاب عليها: {user_data['total_questions']} 📝
• نسبة النجاح: {percentage}% 📈

📚 **التقدم:**
• إجمالي الأسئلة: {TOTAL_QUESTIONS}
• الأسئلة المتبقية: {remaining}
• نسبة الإنجاز: {progress}%

💡 استمر في الإجابة لإكمال جميع الأسئلة!
"""
    
    await update.message.reply_text(stats_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """إلغاء المحادثة"""
    await update.message.reply_text("تم الإلغاء. استخدم /quiz لبدء اختبار جديد.")
    return ConversationHandler.END

def main() -> None:
    """تشغيل البوت"""
    TOKEN = "8583715474:AAEVlFkpMAfTTNCa96AiOUH8qlm7Xuews1w"
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("score", score))
    application.add_handler(CommandHandler("stats", stats))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("quiz", quiz)],
        states={
            ANSWERING: [CallbackQueryHandler(answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    logger.info(f"🤖 البوت يعمل الآن... (عدد الأسئلة: {TOTAL_QUESTIONS})")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
