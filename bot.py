from telegram import Update
from telegram.ext import CallbackContext,ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import datetime
import threading
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# توكن البوت الخاص بك
TOKEN = os.getenv('TOKEN')

NAME, AGE, JOB, HOBBIES, MARRIED, CHILDREN, SKILLS, MONTHLY_GOALS, YEARLY_GOALS = range(9)

def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    update.message.reply_text(
        'مرحباً! أنا بوتك الشخصي. لنبدأ بتوفير بعض المعلومات الشخصية.'
        '\nما اسمك؟'
    )
    return NAME

def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['name'] = update.message.text
    update.message.reply_text(f'مرحباً يا {context.user_data["name"]}! كم عمرك؟')
    return AGE

def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['age'] = update.message.text
    update.message.reply_text('ما هو عملك؟')
    return JOB

def job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['job'] = update.message.text
    update.message.reply_text('هل لديك أي هوايات؟ (يمكنك كتابة أكثر من هواية مفصولة بفاصلة)')
    return HOBBIES

def hobbies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['hobbies'] = update.message.text.split(',')
    update.message.reply_text('هل أنت متزوج/متزوجة؟ (نعم/لا)')
    return MARRIED

def married(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['married'] = update.message.text
    if context.user_data['married'].lower() in ['نعم', 'نعم']:
        update.message.reply_text('هل لديك أولاد؟ (نعم/لا)')
        return CHILDREN
    else:
        update.message.reply_text('ما هي مهاراتك الرئيسية؟ (يمكنك كتابة أكثر من مهارة مفصولة بفاصلة)')
        return SKILLS

def children(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['children'] = update.message.text
    update.message.reply_text('ما هي مهاراتك الرئيسية؟ (يمكنك كتابة أكثر من مهارة مفصولة بفاصلة)')
    return SKILLS

def skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['skills'] = update.message.text.split(',')
    update.message.reply_text('ما هي أهدافك خلال الشهر القادم؟')
    return MONTHLY_GOALS

def monthly_goals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['monthly_goals'] = update.message.text
    update.message.reply_text('ما هي أهدافك خلال العام القادم؟')
    return YEARLY_GOALS

def yearly_goals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['yearly_goals'] = update.message.text
    update.message.reply_text('شكراً لك! لقد أكملت التسجيل بنجاح.')
    set_daily_reminders(update.effective_chat.id, context)
    return ConversationHandler.END

def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    update.message.reply_text('تم إلغاء العملية.')
    return ConversationHandler.END

def set_daily_reminders(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    while True:
        if next_hour < now:
            next_hour += datetime.timedelta(hours=1)
        threading.Timer((next_hour - now).total_seconds(), send_daily_reminder, args=(chat_id, context)).start()
        break

def send_daily_reminder(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    application = context.application
    reminders = [
        "حان وقت صلاة الفجر الآن. هل أكملت الصلاة؟ (نعم/لا)",
        "حان وقت تناول الفطور الآن.",
        "حان وقت صلاة الظهر الآن. هل أكملت الصلاة؟ (نعم/لا)",
        "حان وقت تناول الغداء الآن.",
        "حان وقت صلاة العصر الآن. هل أكملت الصلاة؟ (نعم/لا)",
        "حان وقت تناول العشاء الآن.",
        "حان وقت صلاة المغرب الآن. هل أكملت الصلاة؟ (نعم/لا)",
        "حان وقت صلاة العشاء الآن. هل أكملت الصلاة؟ (نعم/لا)",
        "حان وقت العمل الآن.",
        "حان وقت الدراسة الآن.",
        "حان وقت تقضي وقت مع عائلتك وأصدقائك الآن.",
        "حان وقت الهوايات والترفيه الآن.",
    ]

    for reminder in reminders:
        msg = application.bot.send_message(chat_id=chat_id, text=reminder)
        context.chat_data[f'reminder_{msg.message_id}'] = False

def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_id = update.message.reply_to_message.message_id
    if f'reminder_{message_id}' in context.chat_data:
        response = update.message.text.lower()
        if response in ['نعم', 'لا']:
            context.chat_data[f'reminder_{message_id}'] = response == 'نعم'
            update.message.reply_text('شكراً لك!')
            provide_feedback(update, context, response)
        else:
            update.message.reply_text('رجاءً أجب بـ "نعم" أو "لا".')
    else:
        update.message.reply_text('هذه الرسالة ليست مرتبطة بمهمة.')

def provide_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE, response: str) -> None:
    feedback_messages = {
        "صلاة الفجر": "صلى الله بك! الحمد لله على أنك أكملت الصلاة.",
        "صلاة الظهر": "صلى الله بك! الصلاة في وقتها هي من أفضل الأعمال.",
        "صلاة العصر": "صلى الله بك! استمر في الحفاظ على مواقيت الصلاة.",
        "صلاة المغرب": "صلى الله بك! الصلاة في وقتها هي من أفضل الأعمال.",
        "صلاة العشاء": "صلى الله بك! الصلاة في وقتها هي من أفضل الأعمال.",
        "الفطور": "تناول الفطور مهم جداً! استمتع بالوجبة.",
        "الغداء": "تناول الغداء مهم جداً! استمتع بالوجبة.",
        "العشاء": "تناول العشاء مهم جداً! استمتع بالوجبة.",
        "العمل": "عملك رائع! استمر في الجهد.",
        "الدراسة": "دراسةك مهمة جداً! استمر في التعلم.",
        "وقت مع عائلتك وأصدقائك": "قضاء وقت مع عائلتك وأصدقائك مهم جداً! استمتع!",
        "الهوايات والترفيه": "الهوايات والترفيه مهمان جداً! استمتع!",
    }

    reminders = [
        "صلاة الفجر",
        "الفطور",
        "صلاة الظهر",
        "الغداء",
        "صلاة العصر",
        "العشاء",
        "صلاة المغرب",
        "صلاة العشاء",
        "العمل",
        "الدراسة",
        "وقت مع عائلتك وأصدقائك",
        "الهوايات والترفيه",
    ]

    for reminder in reminders:
        if f'reminder_{update.message.reply_to_message.message_id}' in context.chat_data:
            if context.chat_data[f'reminder_{update.message.reply_to_message.message_id}'] == (response == 'نعم'):
                update.message.reply_text(feedback_messages[reminder])
                break

def end_of_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    completed_tasks = sum(value for key, value in context.chat_data.items() if key.startswith('reminder_'))
    total_tasks = len([key for key in context.chat_data.keys() if key.startswith('reminder_')])
    success_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    report = (
        f"التقرير اليومي:\n"
        f"المهام المكتملة: {completed_tasks}/{total_tasks}\n"
        f"نسبة النجاح: {success_rate:.2f}%\n"
        f"نصائح:\n"
    )

    if success_rate < 50:
        report += "- حاول تحقيق المزيد من المهام في اليوم القادم.\n"
        report += "- إذا كنت واجهت صعوبات، فكر في كيفية تحسين أدائك.\n"
    elif success_rate >= 50 and success_rate < 80:
        report += "- استمر في جهودك! لقد حققت نسبة جيدة.\n"
        report += "- حاول تحسين نسبة الإنجاز قليلاً أكثر.\n"
    else:
        report += "- ممتاز! لقد حققت نسبة عالية جداً!\n"
        report += "- استمر في هذا النمو والاستمرار!\n"

    context.bot.send_message(chat_id=chat_id, text=report)

    # إعادة تعيين بيانات المهام لليوم التالي
    for key in list(context.chat_data.keys()):
        if key.startswith('reminder_'):
            del context.chat_data[key]

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, job)],
            HOBBIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, hobbies)],
            MARRIED: [MessageHandler(filters.TEXT & ~filters.COMMAND, married)],
            CHILDREN: [MessageHandler(filters.TEXT & ~filters.COMMAND, children)],
            SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, skills)],
            MONTHLY_GOALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, monthly_goals)],
            YEARLY_GOALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, yearly_goals)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.REPLY, handle_response))
    application.add_handler(CommandHandler('endofday', end_of_day))

    application.run_polling()

if __name__ == '__main__':
    main()