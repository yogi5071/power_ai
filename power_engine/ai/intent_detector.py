"""
Intent Detector
Power AI Copilot
"""


class IntentDetector:
    """
    Detect user intent based on keywords.
    """

    INTENTS = {

        "battery": [

            "battery",
            "baterai",
            "battery health",
            "backup",
            "backup time",
            "health score",
            "vrla",
            "lithium"

        ],

        "alarm": [

            "alarm",
            "mains fail",
            "genset",
            "rectifier",
            "module fail"

        ],

        "area": [

            "surabaya",
            "malang",
            "sidoarjo",
            "gresik",
            "cluster",
            "kabupaten",
            "kecamatan",
            "wilayah",
            "area"

        ],

        "dashboard": [

            "summary",
            "dashboard",
            "statistik",
            "trend",
            "grafik"

        ]

    }

    @classmethod
    def detect(cls, message: str):

        text = message.lower()

        for intent, keywords in cls.INTENTS.items():

            for keyword in keywords:

                if keyword in text:

                    return intent

        return "general"