# Developer Log

### 2024-07-26
- **ACTION:** Initialized the developer log.
- **ACTION:** Performed a full audit of the codebase from the `Chinegav-git/durak_python_bot` repository.
- **FINDING:** The project uses `aiogram 2.x` and `Pony ORM`. The use of Pony ORM is a deviation from the proposed `SQLAlchemy` stack. This needs to be addressed.
- **FINDING:** The project has a solid, modular structure (`handlers`, `logic`, `db`, `objects`).
- **FINDING:** Initial project documentation was missing.
- **ACTION:** Created project documentation (`ARCHITECTURE.md`, `FEATURES.md`).
- **ACTION:** Created `PROJECT_STANDARDS.md` by adapting the initial prompt to the project's actual technical implementation.
- **BUGFIX:** Fixed an issue where the game turn would incorrectly switch after a player had won in a two-player game. The fix was applied in `durak/logic/actions.py` by adding a condition to terminate the `do_turn` function if the game concludes after a player wins and leaves.
