""" Telegram sender for interacting with the Telegram Bot API using the Aiogram """

from aiogram import Bot
from aiogram.types import URLInputFile, InputMediaPhoto, InputMediaVideo

from telegram.client import telegram_bot
from twitter.models import Tweet, Photo, Video
from twitter.translate import get_translated_tweet_body, get_translated_tweet_header

PARSE_MODE = "HTML"
TYPING_ACTION = "typing"


class TelegramSender:
    """Telegram client for process send to telegram"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(self, chat_id, text, reply_to_message_id=None, disable_web_page_preview=True) -> int:
        """Send a text message to a chat"""
        await self.send_action_typing(chat_id)
        result = await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=reply_to_message_id,
            parse_mode=PARSE_MODE,
            disable_web_page_preview=disable_web_page_preview
        )
        return result.message_id

    async def send_photo(self, chat_id, photo: Photo, caption, reply_to_message_id=None) -> int:
        """Send a photo to a chat"""
        await self.bot.send_chat_action(chat_id=chat_id, action="upload_photo")
        result = await self.bot.send_photo(
            chat_id=chat_id,
            photo=URLInputFile(url = photo.url, bot = self.bot),
            caption=caption,
            reply_to_message_id=reply_to_message_id,
            parse_mode=PARSE_MODE,
        )
        return result.message_id

    async def send_video(self, chat_id, video: Video, caption, reply_to_message_id=None) -> int:
        """Send a video to a chat"""
        await self.bot.send_chat_action(chat_id=chat_id, action="upload_video")
        result = await self.bot.send_video(
            chat_id=chat_id,
            video=URLInputFile(url=video.url, bot = self.bot),
            caption=caption,
            reply_to_message_id=reply_to_message_id,
            parse_mode=PARSE_MODE,
        )
        return result.message_id

    async def send_media_group(self, chat_id, medias: list, text: str, reply_to_message_id=None) -> int:
        """Send a media group to a chat"""
        file = []
        for index, item in enumerate(medias):
            media = URLInputFile(item.url, self.bot)
            if item.type == "photo":
                if index == 0:
                    file.append(InputMediaPhoto(media = media, caption=text, parse_mode=PARSE_MODE))
                else:
                    file.append(InputMediaPhoto(media = media, parse_mode=PARSE_MODE))
            else:
                if index == 0:
                    file.append(InputMediaVideo(media = media, caption=text, parse_mode=PARSE_MODE))
                else:
                    file.append(InputMediaVideo(media = media, parse_mode=PARSE_MODE))

        await self.send_action_typing(chat_id)
        result = await self.bot.send_media_group(
            chat_id=chat_id,
            media=file,
            reply_to_message_id=reply_to_message_id,
        )
        return result[0].message_id

    async def send_poll(self, chat_id, text: str, choices: list, reply_to_message_id=None):
        """Send a typing action to a chat"""
        await self.bot.send_poll(chat_id=chat_id, question=text, options=choices, reply_to_message_id=reply_to_message_id)

    async def send_action_typing(self, chat_id):
        """Send a typing action to a chat"""
        await self.bot.send_chat_action(chat_id=chat_id, action=TYPING_ACTION)

    async def delete(self, message_id, chat_id):
        """Delete a message"""
        await self.bot.delete_message(chat_id=chat_id, message_id=message_id)

    async def send_tweet(self, tweet: Tweet, chat_id, reply_to_message_id, user = None) -> int:
        single_photo = tweet.get_single_photo()
        single_video = tweet.get_single_video()
        poll = tweet.get_poll()
        many_media = tweet.get_multi_media()

        message_head = get_translated_tweet_header(tweet, user, 'ru')
        message_tweet = get_translated_tweet_body(tweet, "ru")
        message_text = f"{message_head}\n\n{message_tweet}".strip()

        if poll is not None:
            message_id = await self.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_to_message_id=reply_to_message_id,
            )
            await self.send_poll(
                chat_id=chat_id,
                text="⬆",
                reply_to_message_id=message_id,
                choices=poll
            )
        elif single_video is not None:
            message_id = await self.send_video(
                chat_id=chat_id,
                video=single_video,
                caption=message_text,
                reply_to_message_id=reply_to_message_id,
            )
        elif single_photo is not None:
            message_id = await self.send_photo(
                chat_id=chat_id,
                photo=single_photo,
                caption=message_text,
                reply_to_message_id=reply_to_message_id,
            )
        elif many_media is not None:
            message_id = await self.send_media_group(
                chat_id=chat_id,
                medias=many_media,
                text=message_text,
                reply_to_message_id=reply_to_message_id,
            )
        else:
            message_id = await self.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_to_message_id=reply_to_message_id,
            )

        return message_id


telegram_sender = TelegramSender(bot=telegram_bot)
