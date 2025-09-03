import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatInviteLink, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Opslag in geheugen
user_progress = {}
user_invite_links = {}

# Groep IDs en private group link
CURRENT_GROUP_ID = -1003031190193  # vervang door je eigen numerieke group_id
PRIVATE_GROUP_LINK = "https://t.me/+4wUs0h5KhYI5MDQx"

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_progress[user_id] = user_progress.get(user_id, 0)

    chat = context.bot.get_chat(CURRENT_GROUP_ID)
    invite = chat.create_invite_link(creates_join_request=False)

    user_invite_links[invite.invite_link] = user_id

    keyboard = [[InlineKeyboardButton(
        f"Share to unlock Instructions ({user_progress[user_id]}/2)",
        url=invite.invite_link
    )]]

    update.message.reply_text(
        "Please share this group to 2 others to unlock the button to get access to our private group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def new_member(update: Update, context: CallbackContext):
    message = update.message
    if message.invite_link:
        invite_link_used = message.invite_link.invite_link
        if invite_link_used in user_invite_links:
            inviter_id = user_invite_links[invite_link_used]
            user_progress[inviter_id] = user_progress.get(inviter_id, 0) + 1
            progress = user_progress[inviter_id]

            if progress < 2:
                keyboard = [[InlineKeyboardButton(
                    f"Share to unlock Instructions ({progress}/2)",
                    url=invite_link_used
                )]]
            else:
                keyboard = [[InlineKeyboardButton("Open private group", url=PRIVATE_GROUP_LINK)]]

            try:
                context.bot.send_message(
                    chat_id=inviter_id,
                    text="✅ Your progress has been updated!",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass

def progress(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    progress_val = user_progress.get(user_id, 0)

    if progress_val < 2:
        invite_link = None
        for link, inviter in user_invite_links.items():
            if inviter == user_id:
                invite_link = link
                break
        keyboard = [[InlineKeyboardButton(
            f"Share to unlock Instructions ({progress_val}/2)",
            url=invite_link if invite_link else "https://t.me/"
        )]]
        update.message.reply_text(
            f"📊 You have invited {progress_val}/2 people so far.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        keyboard = [[InlineKeyboardButton("Open private group", url=PRIVATE_GROUP_LINK)]]
        update.message.reply_text(
            "🎉 You have completed your invites! Click below:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN not set")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("progress", progress))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
