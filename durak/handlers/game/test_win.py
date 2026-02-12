'''
Этот модуль содержит хендлер для тестовой команды /test_win,
которая позволяет администратору мгновенно завершить игру, объявив победителя.
'''

from aiogram import Router, types
from aiogram.filters import Command

from durak.logic.game_manager import get_game_from_context, game_manager

router = Router()


@router.message(Command("test_win"))
async def test_win_handler(message: types.Message):
    '''
    Обработчик команды /test_win.
    Завершает игру и объявляет победителя.
    Использование: /test_win [player_id]
    Если player_id не указан, победителем становится первый игрок.
    '''
    game = get_game_from_context(message.chat.id)
    if not game:
        await message.answer("Игра не найдена в этом чате.")
        return

    # TODO: Добавить проверку на администратора

    try:
        args = message.text.split()
        winner_id = int(args[1]) if len(args) > 1 else None

        # Вызываем новый метод в game_manager
        await game_manager.test_win(game, winner_id)

    except (ValueError, IndexError):
        await message.answer("Неверный формат команды. Используйте: /test_win [player_id]")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
