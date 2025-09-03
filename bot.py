import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatInviteLink
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# Opslag in geheugen
user_progress = {}       # {user_id: int} -> aantal succesvolle invites
user_invite_links = {}   # {invite_link: inviter_id}

# Zet je groeps-ID en private link hier
CURRENT_GROUP_ID = -1003031190193   # <-- vervang door jouw echte group_id (numeriek ID!)
PRIVATE_GROUP_LINK = "https://t.me/+4wUs0h5KhYI5MDQx"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # Progress initialiseren
    user_progress[user_id] = user_progress.get(user_id, 0)

    # Maak unieke invite link voor deze gebruiker
    chat = await context.bot.get_chat(CURRENT_GROUP_ID)
    invite: ChatInviteLink = await chat.create_invite_link(
        creates_join_request=False,
        member_limit=0,
        expire_date=None
    )

    # Sla op wie bij welke link hoort
    user_invite_links[invite.invite_link] = user_id

    # Stuur bericht met knop
    keyboard = [
        [InlineKeyboardButton(
            f"Share to unlock Instructions ({user_progress[user_id]}/2)",
            url=invite.invite_link
        )]
    ]
    await update.message.reply_text(
        "Please share this group to 2 others to unlock the button to get access to our private group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wordt aangeroepen als iemand joint via een invite link"""
    chat_join_request = update.message
    if chat_join_request is None:
        return

    if chat_join_request.invite_link:
        invite_link_used = chat_join_request.invite_link.invite_link
        if invite_link_used in user_invite_links:
            inviter_id = user_invite_links[invite_link_used]
            user_progress[inviter_id] = user_progress.get(inviter_id, 0) + 1

            # Update knop voor de inviter
            progress = user_progress[inviter_id]
            if progress < 2:
                keyboard = [
                    [InlineKeyboardButton(
                        f"Share to unlock Instructions ({progress}/2)",
                        url=invite_link_used
                    )]
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("Open private group", url=PRIVATE_GROUP_LINK)]
                ]

            try:
                await context.bot.send_message(
                    chat_id=inviter_id,
                    text="✅ Your progress has been updated!",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass  # Als DM niet werkt, gewoon negeren


async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Laat een gebruiker zijn voortgang zien"""
    user_id = update.effective_user.id
    progress = user_progress.get(user_id, 0)

    if progress < 2:
        invite_link = None
        # Zoek invite link van deze gebruiker
        for link, inviter in user_invite_links.items():
            if inviter == user_id:
                invite_link = link
                break

        keyboard = [
            [InlineKeyboardButton(
                f"Share to unlock Instructions ({progress}/2)",
                url=invite_link if invite_link else "https://t.me/"
            )]
        ]
        await update.message.reply_text(
            f"📊 You have invited {progress}/2 people so far.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        keyboard = [
            [InlineKeyboardButton("Open private group", url=PRIVATE_GROUP_LINK)]
        ]
        await update.message.reply_text(
            "🎉 You have completed your invites! Click below:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN not set")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

    app.run_polling()


if __name__ == "__main__":
    main()
