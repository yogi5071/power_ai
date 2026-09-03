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

    # ==========================================================
    # STATE
    # ==========================================================

    def set_state(self, user_id, state):

        session = self.sessions.setdefault(
            user_id,
            {}
        )

        session["state"] = state

    def get_state(self, user_id):

        session = self.sessions.get(user_id)

        if not session:
            return ConversationState.NONE

        return session.get(
            "state",
            ConversationState.NONE
        )

    # ==========================================================
    # CONTEXT
    # ==========================================================

    def set_context(
        self,
        user_id,
        intent=None,
        scope_type=None,
        scope_value=None,
        status=None,
        year=None,
        site_id=None,
        period_months=None,
        bot_message_id=None,
        pln_variable_query=None,
    ):

        session = self.sessions.setdefault(
            user_id,
            {}
        )

        context = session.setdefault(
            "context",
            {}
        )

        # ------------------------------------------------------
        # GENERAL CONTEXT
        # ------------------------------------------------------

        if intent is not None:

            context["intent"] = intent

        if scope_type is not None:

            context["scope_type"] = scope_type

        if scope_value is not None:

            context["scope_value"] = scope_value

        if status is not None:

            context["status"] = status

        if year is not None:

            context["year"] = year

        if site_id is not None:

            context["site_id"] = site_id

        if period_months is not None:

            context["period_months"] = period_months

        if bot_message_id is not None:

            context["bot_message_id"] = bot_message_id

        # ------------------------------------------------------
        # PLN VARIABLE QUERY
        #
        # Digunakan untuk menyimpan parameter query PLN
        # ketika user melakukan pertanyaan seperti:
        #
        # "site mana yang KWH di atas 5000?"
        #
        # atau:
        #
        # "site mana yang tagihannya di bawah 1 juta
        #  di NOP SBY?"
        #
        # Context ini kemudian digunakan ketika user melakukan
        # follow-up:
        #
        # "site mana saja?"
        #
        # sehingga user tidak perlu mengulang pertanyaan awal.
        # ------------------------------------------------------

        if pln_variable_query is not None:

            context["pln_variable_query"] = (
                pln_variable_query.copy()
                if isinstance(
                    pln_variable_query,
                    dict
                )
                else pln_variable_query
            )

    # ==========================================================
    # GET CONTEXT
    # ==========================================================

    def get_context(self, user_id):

        session = self.sessions.get(user_id)

        if not session:

            return {}

        return session.get(
            "context",
            {}
        ).copy()

    # ==========================================================
    # GET PLN VARIABLE QUERY
    #
    # Helper khusus PLN variable query.
    #
    # Mengembalikan parameter query terakhir yang disimpan
    # untuk user tersebut.
    # ==========================================================

    def get_pln_variable_query(self, user_id):

        context = self.get_context(
            user_id
        )

        query = context.get(
            "pln_variable_query"
        )

        if not query:

            return {}

        if isinstance(
            query,
            dict
        ):

            return query.copy()

        return query

    # ==========================================================
    # CLEAR PLN VARIABLE QUERY
    # ==========================================================

    def clear_pln_variable_query(self, user_id):

        session = self.sessions.get(
            user_id
        )

        if not session:

            return

        context = session.get(
            "context"
        )

        if not context:

            return

        context.pop(
            "pln_variable_query",
            None
        )

    # ==========================================================
    # CLEAR CONTEXT
    # ==========================================================

    def clear_context(self, user_id):

        session = self.sessions.get(user_id)

        if not session:

            return

        session["context"] = {}

    # ==========================================================
    # CLEAR EVERYTHING
    # ==========================================================

    def clear(self, user_id):

        self.sessions.pop(
            user_id,
            None
        )

    # ==========================================================
    # CHECK EXISTING CONTEXT
    # ==========================================================

    def has_context(self, user_id):

        session = self.sessions.get(user_id)

        if not session:

            return False

        context = session.get(
            "context",
            {}
        )

        return bool(context)

    # ==========================================================
    # CHECK PLN VARIABLE QUERY
    # ==========================================================

    def has_pln_variable_query(self, user_id):

        query = self.get_pln_variable_query(
            user_id
        )

        return bool(query)