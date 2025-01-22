from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """
    Represents the states associated with the user interaction.

    This class defines the states that are part of the user's workflow. Each state
    represents a specific point in the process where the bot is waiting for user
    input or performing a task.

    States:
        waiting_username (State): State when the bot is waiting for the user to
                                    provide their username.
    """

    waiting_username = State()
