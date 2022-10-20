import os
import sys
import random
import asyncio

from typing import Union
from collections import deque
from config import token, owner_id
from custom_libs.custom_cfg import custom_settings

from vkbottle.dispatch.rules import ABCRule
from vkbottle.exception_factory import VKAPIError
from vkbottle.bot import Bot, Message, run_multibot
from vkbottle import API, Keyboard, KeyboardButtonColor, Text
from vkbottle.tools.dev.mini_types.base import BaseMessageMin

# Настройка по конфигу

bot=Bot()

# Кастомный рулз для вызова по ID
class FromIdRule(ABCRule[BaseMessageMin]):
    def __init__(self, from_id: Union[list[int], int]):
        self.from_id = from_id

    async def check(self, event: BaseMessageMin) -> Union[dict, bool]:
        return event.from_id in self.from_id

bot.labeler.custom_rules['from_id'] = FromIdRule

#################################### Кнопки #########################################################################

# Цвета кнопок
async def button_colors_choose(color_choose):
    button_main_colors = [KeyboardButtonColor.POSITIVE, KeyboardButtonColor.NEGATIVE, KeyboardButtonColor.PRIMARY, KeyboardButtonColor.SECONDARY]
    return button_main_colors[color_choose]

# Режим кнопок 1 - стандартный режим
async def classic_mode(keyboard, message_counter, custom_command):
    for row in range(0, 10):
        button_colors = deque([
                await button_colors_choose(custom_settings[custom_command]['mode1_button_colors'][0]),
                await button_colors_choose(custom_settings[custom_command]['mode1_button_colors'][1]),
                await button_colors_choose(custom_settings[custom_command]['mode1_button_colors'][2]),
                await button_colors_choose(custom_settings[custom_command]['mode1_button_colors'][3])
            ])
        button_text = deque([
                custom_settings[custom_command]['mode1_2_3_buttons_text'][0],
                custom_settings[custom_command]['mode1_2_3_buttons_text'][1],
                custom_settings[custom_command]['mode1_2_3_buttons_text'][2],
                custom_settings[custom_command]['mode1_2_3_buttons_text'][3]
            ])
        button_colors.rotate(message_counter % 4)
        button_text.rotate(message_counter % 4)
        for button_add in range(0, 4):
            keyboard.add(Text(button_text[button_add]), color = button_colors[button_add])
        if row != 9:
            keyboard.row()

# Режим кнопок 2 - режим радуги
async def rainbow_mode(keyboard, message_counter, custom_command):
    for row in range(0, 10):
        button_colors = deque([
                await button_colors_choose(0),
                await button_colors_choose(1),
                await button_colors_choose(2),
                await button_colors_choose(3)
            ])
        button_colors.rotate((message_counter + row) % 4)
        for button_add in range(0, 4):
            keyboard.add(Text(custom_settings[custom_command]['mode1_2_3_buttons_text'][button_add]), color = button_colors[button_add])
        if row != 9:
            keyboard.row()

# Режим кнопок 3 - режим вируса
async def virus_mode(keyboard, custom_command):
    for row in range(0, 10):
        for button_add in range(0, random.randint(1, 4)):
            keyboard.add(Text(custom_settings[custom_command]['mode1_2_3_buttons_text'][random.randint(0, 3)]), color = await button_colors_choose(random.randint(0, 2)))
        if row != 9:
            keyboard.row()

# Режим кнопок 4 - режим из бота спарты
async def sparta_raid_mode(keyboard):
    temp = 1
    rand_temp = random.randint(1, 12)
    for row in range(0, 3):
        button_text = [
                'bosslike.ru',
                'olike.ru',
                'vto.pe'
            ]
        for button_add in range(0, 4):
            if temp == rand_temp:
                keyboard.add(Text('stop'), color=KeyboardButtonColor.POSITIVE)
            else:
                keyboard.add(Text(button_text[random.randint(0, 2)]), color=KeyboardButtonColor.NEGATIVE)
            temp += 1
        if row != 2:
            keyboard.row()

# Выбор режима кнопок
async def button_modes_choose(keyboard, message_counter, custom_command):
    match custom_settings[custom_command]['button_mode']:
        case 1:
            await classic_mode(keyboard, message_counter, custom_command)
        case 2:
            await rainbow_mode(keyboard, message_counter, custom_command)
        case 3:
            await virus_mode(keyboard, custom_command)
        case 4:
            await sparta_raid_mode(keyboard)
        case _:
            return

#################################### Текст ##########################################################################

# Режим текста 1 - стандартный режим, спам всем текстом из конфига
async def standart_text_mode(custom_command, text = []):
    text.append(custom_settings[custom_command]['text'])
    return text

# Режим текста 2 - режим по строчно, спам по каждой строчки в конфиге
async def line_by_line_text_mode(custom_command, text = []):
    temp_letter = ''
    counter = 0
    for letter in custom_settings[custom_command]['text']:
        if letter != '\n':
            temp_letter += letter
        elif letter == custom_settings[custom_command]['text'][counter - 1] and letter == '\n':
            text.append('ᅠ')
        else:
            text.append(temp_letter)
            temp_letter = ''
        counter += 1
    text.append(temp_letter)
    return text

# Режим текста 3 - режим обрезки через символ, спам по каждой обрезки из конфига
async def cut_text_mode(custom_command, text = []):
    temp_letter = ''
    counter = 0
    for letter in custom_settings[custom_command]['text']:
        if letter != '\\':
            temp_letter += letter
        elif letter == custom_settings[custom_command]['text'][counter - 1] and letter == '\\':
            text.append('ᅠ')
        else:
            text.append(temp_letter)
            temp_letter = ''
        counter += 1
    text.append(temp_letter)
    return text

# Выбор режима текста и вложения
async def text_modes_choose(custom_command):
    match custom_settings[custom_command]['text_mode']:
        case 2:
            text = await line_by_line_text_mode(custom_command)
        case 3:
            text = await cut_text_mode(custom_command)
        case _:
            text = await standart_text_mode(custom_command)
    return text

# Режим случайного текста или вложения
async def random_value(message_counter, choose, len_list):
    match choose:
        case False:
            return message_counter % len_list
        case True:
            return random.randint(0, len_list - 1)

#################################### From id list ###################################################################

from_id_list = []
for i in custom_settings:
    for number in range(0, len(custom_settings[i]['call_from_id'])):
        from_id_list.append(custom_settings[i]['call_from_id'][number])

#################################### Команды для вызова #############################################################

# Берёт команды из конфига

command_list = []
for i in custom_settings:
    command_list.append(f'/{i}')

#################################### Сердце бота ####################################################################

# Проверка на ID в списке локальной настройки
async def id_checker(custom_command, config_value, id_to_check):
    for i in range(0, len(custom_settings[custom_command][config_value])):
        try:
            if id_to_check == custom_settings[custom_command][config_value][i]:
                return True
        except: pass
    return False

# Основной спам механизм
@bot.on.message(text = command_list)
async def send_message(message: Message):
    custom_command = message.text[1:]
    message_counter = 0
    text = await text_modes_choose(custom_command)
    infinity_spammer = await id_checker(custom_command, 'call_from_id', message.from_id) and await id_checker(custom_command, 'group_id', message.group_id) or custom_settings[custom_command]['any'] and await id_checker(custom_command, 'group_id', message.group_id)
    while infinity_spammer:
        keyboard = Keyboard(one_time=False)
        try:
            await button_modes_choose(keyboard, message_counter, custom_command)
            await message.answer(
                message = text[await random_value(message_counter, custom_settings[custom_command]['random_text'], len(text))],
                attachment = custom_settings[custom_command]['attachment'][await random_value(message_counter, custom_settings[custom_command]['random_attachment'], len(custom_settings[custom_command]['attachment']))],
                keyboard = keyboard.get_json()
            )
            message_counter += 1
            if message_counter == custom_settings[custom_command]['message_counter_limit']:
                print('Stopped spamming by counter')
                break
            await asyncio.sleep(custom_settings[custom_command]['delay'])
        except VKAPIError[100]:
            await message.answer(
                message='ᅠ',
                keyboard=keyboard.get_json()
            )
            message_counter += 1
            if message_counter == custom_settings[custom_command]['message_counter_limit']:
                print('Stopped spamming by counter')
                break
            await asyncio.sleep(custom_settings[custom_command]['delay'])
        except VKAPIError[7, 917, 945, 946] as e:
            print(f'Stopped spamming, reason: {e}')
            break
        except VKAPIError as e:
            print(f"Can't send message, reason: {e}")
            await asyncio.sleep(custom_settings[custom_command]['delay_error'])

# Перезапускает бота
@bot.on.message(from_id = owner_id, command = 'restart')
async def restart_application(message: Message):
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

#################################### Основная настройка перед запуском ##############################################

if __name__ == '__main__':
    apies = []
    for i in range(0, len(token)):
        apies.append(API(token))
    bot.loop_wrapper.auto_reload = True
    run_multibot(bot, apis = apies)
