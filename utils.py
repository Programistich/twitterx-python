from aiogram import types


def get_text_from_bot_command(message: types.Message) -> str:
    if message.entities is None:
        return message.text

    bot_command = list(filter(lambda entity: entity.type == "bot_command", message.entities))[0]
    bot_command_text = message.text[bot_command.offset:bot_command.offset + bot_command.length]
    return message.text.replace(bot_command_text + " ", "")
