from aiogram import types
from textwrap import dedent
from loader import bot, dp, Commands

@dp.message_handler(commands=[Commands.IGOR, Commands.GRINA])
async def IGOR(message: types.Message):
    igor_text = dedent(f"@grina4891grina - самий сексуальний дельфін в чаті 🐬 ")
    await message.answer(igor_text)