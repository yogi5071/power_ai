from enum import Enum


class Intent(Enum):
    GREETING = "GREETING"

    BATTERY = "BATTERY"

    ALARM = "ALARM"

    SITE = "SITE"

    RECTIFIER = "RECTIFIER"

    GENSET = "GENSET"

    GENERAL_AI = "GENERAL_AI"

    UNKNOWN = "UNKNOWN"