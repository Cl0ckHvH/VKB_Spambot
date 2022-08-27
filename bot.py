import asyncio
import random
import loguru
import typing
import toml
import time
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
    if "token" in os.environ:
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

async def button_colors_choose(color_choose):
    button_main_colors = deque(
        [
            KeyboardButtonColor.POSITIVE, KeyboardButtonColor.NEGATIVE, KeyboardButtonColor.PRIMARY, KeyboardButtonColor.SECONDARY
        ]
    )
    return button_main_colors[color_choose]

async def classic_mode(keyboard, message_counter):
    for row in range(0, 10):
        button_colors = deque(
            [
                await button_colors_choose(int(config["mode1_4_button_color1"])),
                await button_colors_choose(int(config["mode1_button_color2"])),
                await button_colors_choose(int(config["mode1_button_color3"])),
                await button_colors_choose(int(config["mode1_button_color4"]))
            ]
        )
        button_text = deque(
            [
                config["mode1_2_3_4_button_text1"],
                config["mode1_2_3_button_text2"],
                config["mode1_2_3_button_text3"],
                config["mode1_2_3_button_text4"]
            ]
        )
        button_colors.rotate(message_counter % 4)
        button_text.rotate(message_counter % 4)
        for button_add in range(0, 4):
            keyboard.add(Text(button_text[button_add]), color = button_colors[button_add])
        if row != 9:
            keyboard.row()

async def rainbow_mode(keyboard, message_counter):
    for row in range(0, 10):
        button_colors = deque(
            [
                await button_colors_choose(0),
                await button_colors_choose(1),
                await button_colors_choose(2),
                await button_colors_choose(3)
            ]
        )
        button_text = deque(
            [
                config["mode1_2_3_4_button_text1"],
                config["mode1_2_3_button_text2"],
                config["mode1_2_3_button_text3"],
                config["mode1_2_3_button_text4"]
            ]
        )
        button_colors.rotate((message_counter + row) % 4)
        for button_add in range(0, 4):
            keyboard.add(Text(button_text[button_add]), color = button_colors[button_add])
        if row != 9:
            keyboard.row()

async def virus_mode(keyboard):
    for row in range(0, 10):
        button_text = deque(
            [
                config["mode1_2_3_4_button_text1"],
                config["mode1_2_3_button_text2"],
                config["mode1_2_3_button_text3"],
                config["mode1_2_3_button_text4"]
            ]
        )
        for button_add in range(0, random.randint(1, 4)):
            keyboard.add(Text(button_text[random.randint(0, 3)]), color = await button_colors_choose(random.randint(0, 2)))
        if row != 9:
            keyboard.row()

async def fake_stop_mode(keyboard):
    keyboard.add(Text(config["mode1_2_3_4_button_text1"], payload = {"cmd": "stop_button"}), color = await button_colors_choose(int(config["mode1_4_button_color1"])),)
    return

async def sparta_raid_mode(keyboard):
    temp = 1
    rand_temp = random.randint(1, 12)
    for row in range(0, 3):
        button_text = deque(
            [
                "bosslike.ru",
                "olike.ru",
                "vto.pe"
            ]
        )
        for button_add in range(0, 4):
            if temp == rand_temp:
                keyboard.add(Text("stop"), color=KeyboardButtonColor.POSITIVE)
            else:
                keyboard.add(Text(button_text[random.randint(0, 2)]), color=KeyboardButtonColor.NEGATIVE)
            temp += 1
        if row != 2:
            keyboard.row()

async def button_modes_choose(choose, keyboard, message_counter):
    match choose:
        case 1:
            await classic_mode(keyboard, message_counter)
        case 2:
            await rainbow_mode(keyboard, message_counter)
        case 3:
            await virus_mode(keyboard)
        case 4:
            await fake_stop_mode(keyboard)
        case 5:
            await sparta_raid_mode(keyboard)
        case _:
            print ("Keyboard is off")
            return

async def standart_text_mode(text):
    text.append("")
    text[0] = config["text"]
    return

async def line_by_line_text_mode(text):
    text.append("")
    a = 0
    counter = 0
    for row in config["text"]:
        if row != '\n':
            text[a] += row
        elif row == config["text"][counter - 1] and row == '\n':
            text[a] = "ᅠ"
            text.append("")
            a += 1
        else:
            text.append("")
            a += 1
        counter += 1
    return

async def cut_text_mode(text):
    text.append("")
    a = 0
    counter = 0
    for row in config["text"]:
        if row != 'ᅠ':
            text[a] += row
        elif row == config["text"][counter - 1] and row == 'ᅠ':
            text[a] = "ᅠ"
            text.append("")
            a += 1
        else:
            text.append("\n")
            a += 1
        counter += 1

async def text_and_attachment_modes_choose(choose, text, document):
    document.append("")
    a = 0
    counter = 0
    for row in config["attachment"]:
        if row != '\n':
            document[a] += row
        elif row == config["attachment"][counter - 1] and row == '\n':
            document[a] = ""
        else:
            document.append("")
            a += 1
        counter += 1
    match choose:
        case 2:
            await line_by_line_text_mode(text)
            return
        case 3:
            await cut_text_mode(text)
            return
        case _:
            await standart_text_mode(text)
            return

async def random_text(message_counter, choose, len_text):
    match choose:
        case 0:
            return message_counter % len_text
        case _:
            return random.randint(0, len_text - 1)

async def random_attachment(message_counter, choose, len_attachment):
    match choose:
        case 0:
            return message_counter % len_attachment
        case _:
            return random.randint(0, len_attachment - 1)

message_counter = 0
text = []
document = []
@bot.on.chat_message(from_id = int(config["call_from_id"]), action = "chat_invite_user")
@bot.on.chat_message(from_id = int(config["call_from_id"]), command = config["call_command"])
async def send_message(message: Message):
    global message_counter
    global text
    global document
    while True:
        try:
            keyboard = Keyboard(one_time = False)
            await button_modes_choose(int(config["button_mode"]), keyboard, message_counter)
            await bot.api.messages.send(
                random_id = random.getrandbits(31) * random.choice([-1, 1]),
                peer_id = message.peer_id,
                message = text[await random_text(message_counter, int(config["random_text"]), len(text))],
                attachment = document[await random_attachment(message_counter, int(config["random_attachment"]), len(document))],
                keyboard = keyboard.get_json()
            )
            message_counter += 1
            if message_counter == int(config["message_counter_limit"]):
                print("Stopped spamming by counter")
                message_counter = 0
                break
            await asyncio.sleep(float(config["delay"]))
        except VKAPIError[7]:
            print("Stopped spamming, reason: bot was kicked from conversation")
            break
        except VKAPIError[945]:
            print("Stopped spamming, reason: chat was disabled")
            break
        except VKAPIError as e:
            print("Can't send message, reason: ", e)
            await asyncio.sleep(float(config["delay_kill"]))

@bot.on.chat_message(payload = {"cmd": "stop_button"})
async def fake_stop(message: Message):
    global message_counter
    if message_counter:
        keyboard = Keyboard(one_time=False)
        await bot.api.messages.send(
            random_id = random.getrandbits(31) * random.choice([-1, 1]),
            peer_id = message.peer_id,
            message = config["mode_4_text"],
            keyboard = keyboard.get_json()
        )
        time.sleep(float(config["delay_stop"]))

async def setup_settings():
    global text
    global document
    await text_and_attachment_modes_choose(int(config["text_mode"]), text, document)

if __name__ == "__main__":
    setup = asyncio.get_event_loop()
    setup.run_until_complete(setup_settings())
    bot.loop_wrapper.auto_reload = True
    bot.run_forever()
