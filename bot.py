import asyncio
import random
import loguru
import typing
import toml
import os
from collections import deque
from typing import Union
from loguru import logger

from vkbottle import API, bot, Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle.tools.dev.mini_types.base import BaseMessageMin
from vkbottle.exception_factory import VKAPIError
from vkbottle.modules import logger

with open("config.toml", "r", encoding="utf-8") as f:
    if "message_text" in os.environ and "token" in os.environ:
        config = dict(os.environ)
        for key, value in toml.load(f).items():
            if key not in config:
                config[key] = value
    else:
        config = toml.load(f)

bot=Bot(token=config["token"])

class FromIdRule(ABCRule[BaseMessageMin]):
    def __init__(self, from_id: int = 0):
        self.from_id = from_id

    async def check(self, event: BaseMessageMin) -> Union[dict, bool]:
        return self.from_id == (event.from_id)

bot.labeler.custom_rules["from_id"] = FromIdRule

async def classic_mode(keyboard, message_counter):
    for row in range(0, 10):
        button_main_colors = deque(
            [
                KeyboardButtonColor.POSITIVE,
                KeyboardButtonColor.NEGATIVE,
                KeyboardButtonColor.PRIMARY,
                KeyboardButtonColor.SECONDARY
            ]
        )
        button_colors = deque(
            [
                button_main_colors[int(config["mode1_button_color1"])],
                button_main_colors[int(config["mode1_button_color2"])],
                button_main_colors[int(config["mode1_button_color3"])],
                button_main_colors[int(config["mode1_button_color4"])]
            ]
        )
        button_text = deque(
            [
                config["mode1_button_text1"],
                config["mode1_button_text2"],
                config["mode1_button_text3"],
                config["mode1_button_text4"]
            ]
        )
        button_colors.rotate(message_counter % 4)
        button_text.rotate(message_counter % 4)
        for button_add in range(0, 4):
            keyboard.add(Text(button_text[button_add]), color = button_colors[button_add])
        if row != 9:
            keyboard.row()
    
async def button_modes_choose(choose, keyboard, message_counter):
    match choose:
        case 1:
            await classic_mode(keyboard, message_counter)
        case _:
            print ("Keyboard is off")
            return

@bot.on.message(from_id = int(config["call_from_id"]), action = "chat_invite_user")
@bot.on.message(from_id = int(config["call_from_id"]), command = config["call_command"])
async def send_message(message: Message):
    message_counter = 0
    while True:
        try:
            keyboard = Keyboard(one_time = False)
            await button_modes_choose(int(config["button_mode"]), keyboard, message_counter)
            await bot.api.messages.send(
                random_id=random.getrandbits(31) * random.choice([-1, 1]),
                peer_id = message.peer_id,
                message = config["text"],
                attachment = config["attachment"],
                keyboard = keyboard.get_json()
            )
            message_counter += 1
            if message_counter == int(config["message_counter_limit"]):
                print("Stopped spamming by counter")
                break
            await asyncio.sleep(float(config["delay"]))
        except VKAPIError[7] as e:
            print("Stopped spamming, reason: bot was kicked from conversation")
            break
        except VKAPIError[945] as e:
            print("Stopped spamming, reason: chat was disabled")
            break
        except VKAPIError as e:
            print("Can't send message, reason: ", e)
            await asyncio.sleep(float(config["delay_kill"]))

if __name__ == "__main__":
    bot.loop_wrapper.auto_reload = True
    bot.run_forever()