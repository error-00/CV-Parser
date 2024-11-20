from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from resume_parser import fetch_resumes

from config import TELEGRAM_TOKEN

# Define states
(
    SELECTING_SITE,
    ENTERING_JOB_POSITION,
    ENTERING_LOCATION,
    ENTERING_EXPERIENCE,
    ENTERING_SALARY,
) = range(5)


# Start command
async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Work.ua", callback_data="work_ua")],
        [InlineKeyboardButton("Robota.ua", callback_data="robota_ua")],
        [InlineKeyboardButton("All", callback_data="all")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a job site:", reply_markup=reply_markup)
    return SELECTING_SITE


# Handle site selection
async def handle_site_selection(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["site"] = query.data
    await query.edit_message_text("Please enter the job position you are looking for:")
    return ENTERING_JOB_POSITION


# Handle user input for job position
async def handle_job_position(update, context):
    context.user_data["job_position"] = update.message.text
    await update.message.reply_text("Please enter the location (optional, write '-'):")
    return ENTERING_LOCATION


# Handle user input for location
async def handle_location(update, context):
    context.user_data["location"] = (
        update.message.text if update.message.text != "-" else None
    )
    await update.message.reply_text(
        "Please enter the experience level/range (optional, write '-'):"
    )
    return ENTERING_EXPERIENCE


# Handle user input for experience level
async def handle_experience(update, context):
    experience_input = update.message.text
    if experience_input == "-":
        context.user_data["experience"] = None
    else:
        try:
            # Handle case where the experience is entered as a number or range (e.g., "2-5 years")
            context.user_data["experience"] = experience_input
        except ValueError:
            await update.message.reply_text(
                "Invalid experience range, please enter a valid value."
            )
            return ENTERING_EXPERIENCE

    await update.message.reply_text(
        "Please enter the salary range (optional, write '-'):"
    )
    return ENTERING_SALARY


# Handle user input for salary range
async def handle_salary(update, context):
    if "site" not in context.user_data:
        await update.message.reply_text("Please select a job site first using /start.")
        return

    salary_input = update.message.text
    if salary_input == "-":
        context.user_data["salary"] = None
    else:
        context.user_data["salary"] = salary_input

    site = context.user_data.get("site")
    job_position = context.user_data.get("job_position")
    location = context.user_data.get("location")
    experience = context.user_data.get("experience")
    salary = context.user_data.get("salary")
    await update.message.reply_text(f"Fetching resumes for '{job_position}'...")

    # Fetch resumes
    try:
        resumes = fetch_resumes(
            site,
            job_position=job_position,
            location=location,
            experience=experience,
            salary=salary,
        )

        if resumes:
            for resume in resumes[:5]:
                await update.message.reply_text(
                    f"Title: {resume['title']}\n"
                    f"Salary: {resume['salary']}\n"
                    f"Personal Info: {resume['personal_info']}\n"
                    f"Location: {resume['location']}\n"
                    f"Link: {resume['link']}\n"
                    f"Score: {resume['score']}\n"
                )
        else:
            await update.message.reply_text("No resumes found.")

    except Exception as e:
        await update.message.reply_text(
            f"Error occurred while fetching resumes: {str(e)}"
        )

    return ConversationHandler.END


# Help command
async def help_command(update, context):
    await update.message.reply_text("Use /start to begin.")


# Define the conversation handler
def main():
    # Initialize the Application object with the provided token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Create a conversation handler to handle multiple steps
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_SITE: [CallbackQueryHandler(handle_site_selection)],
            ENTERING_JOB_POSITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_job_position)
            ],
            ENTERING_LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_location)
            ],
            ENTERING_EXPERIENCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_experience)
            ],
            ENTERING_SALARY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_salary)
            ],
        },
        fallbacks=[CommandHandler("help", help_command)],
    )

    # Add the conversation handler to the application
    application.add_handler(conversation_handler)

    # Start polling for updates
    application.run_polling()


if __name__ == "__main__":
    main()
