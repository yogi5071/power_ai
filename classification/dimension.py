from enum import Enum


class Dimension(str, Enum):

    SITE = "site"

    KABUPATEN = "kabupaten"

    KECAMATAN = "kecamatan"

    CLUSTER = "cluster"

    NOP = "nop"

    BATTERY = "battery"

    RECTIFIER = "rectifier"

    TECHNOLOGY = "technology"

    WARRANTY = "warranty"

    UNKNOWN = "unknown"