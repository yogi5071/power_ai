from enum import Enum


class ConversationState(Enum):

    NONE = 0

    WAITING_BATTERY_SITE = 1

    WAITING_ALARM_SITE = 2

    WAITING_SITE_DETAIL = 3

    WAITING_RECTIFIER_SITE = 4


class ConversationManager:

    def __init__(self):

        self.sessions = {}

    def set_state(self, user_id, state):

        self.sessions[user_id] = state

    def get_state(self, user_id):

        return self.sessions.get(
            user_id,
            ConversationState.NONE
        )

    def clear_state(self, user_id):

        self.sessions[user_id] = ConversationState.NONE