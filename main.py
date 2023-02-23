import asyncio
import random
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, Text
from aiogram.types import Message
from aiogram.types import ContentType
from aiogram import F
from dataclasses import dataclass


# Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
API_TOKEN: str = '6138908819:AAG_t-9X6Pl_sKG15e1MqS-kkzchbLCDq0k'

# Создаем объекты бота и диспетчера
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()

ATTEMPTS: int = 5
users: dict = {}

@dataclass
class User():
    name: str
    stat_number: int
    in_game: bool
    attemps_ramain: int
    total_games: int
    wins: int
    secret_number: int


def get_random_number() -> int:
    return random.randint(1, 100)


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    user = User(name=message.from_user.full_name,
                in_game=False,
                attemps_ramain=ATTEMPTS,
                total_games=0,
                wins=0,
                secret_number=0,
                stat_number=len(users) + 1)
    users[message.from_user.id] = user
    print(f'Подключился игрок {message.from_user.username}')
    await message.answer(f'Привет!\nТы игрок № {user.stat_number}\nНапиши /help чтобы узнать правила игры')


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
                         f'а вам нужно его угадать\nУ вас есть {ATTEMPTS} '
                         f'попыток\n\nДоступные команды:\n/help - правила '
                         f'игры и список команд\n/cancel - выйти из игры\n'
                         f'/stat - посмотреть статистику\n\nДавай сыграем?\n'
                         f'Напишите мне "давай" или "игра" чтобы начать')

# Этот хэндлер будет срабатывать на команду "/stat"
@dp.message(Command(commands=['stat']))
async def process_stat_command(message: Message):
    user_id = message.from_user.id
    user = users[user_id]
    await message.answer(f'Всего игр сыграно: {user.total_games}\n'
                         f'Игр выиграно: {user.wins}')

@dp.message(Text(text=['Да', 'Давай', 'Сыграем', 'Игра',
                       'Играть', 'Хочу играть', 'ок'], ignore_case=True))
async def process_positive_answer(message: Message):
    user_id = message.from_user.id
    user = users[user_id]
    if not user.in_game:
        user.in_game = True
        user.secret_number = get_random_number()
        user.attemps_ramain = ATTEMPTS
        await message.answer(f'Ура! я загадал число. Отгадай его за {user.attemps_ramain} попыток, и будешь большим молодцом')
    else:
        await message.answer('Пока мы играем в игру я могу '
                             'реагировать только на числа от 1 до 100 '
                             'и команду /stat')

# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_numbers_answer(message: Message):
    user_id = message.from_user.id
    user = users[user_id]
    ans = int(message.text)
    if user.in_game:

        if ans == user.secret_number:
            user.in_game = False
            user.total_games += 1
            user.wins += 1
            print(f'Игрок {user.name} выиграл!')
            await message.reply(f'Ура! Вы отгадали число!\nМожет еще разок?')
        elif ans > user.secret_number:
            user.attemps_ramain -= 1
            await message.answer(f'Загаданное число меньше')
        elif ans < user.secret_number:
            user.attemps_ramain -= 1
            await message.answer(f'Загаданное число больше')

        if user.attemps_ramain == 0:
            print(f'Игрок {user.name} проиграл :(')
            user.in_game = False
            user.total_games += 1
            await message.answer(f'Увы! Вы проиграли. Мое число было {user.secret_number}\n'
                                 f'Сыграем еще раз? Напишите "ок" для начала новой игры')
        if user.in_game and user.attemps_ramain == 1:
            await message.answer(f'Сейчас сосредоточься, осталась 1 попытка!')

    else:
        await message.answer('Мы еще не играем, напишите "да" или "игра", чтобы начать')



# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
@dp.message()
async def send_echo(message: Message):
    await message.reply(text='Я не понимаю чего вы от меня хотите. Попробуйте написать "да" или "игра" для старта, или '
                             '\\stat для статистики')

if __name__ == '__main__':
    dp.run_polling(bot)
