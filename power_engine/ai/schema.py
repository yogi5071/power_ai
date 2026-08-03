"""
Schema yang menjelaskan field apa saja
yang boleh digunakan AI ketika membuat query.
"""


BATTERY_SCHEMA = {
    "table": "battery",

    "fields": {

        "site": "siteid",
        "site_id": "siteid",
        "siteid": "siteid",

        "kabupaten": "kabupaten",
        "kecamatan": "kecamatan",
        "cluster": "cluster",

        "technology": "technology",
        "jenis battery": "technology",
        "battery": "technology",

        "vendor": "vendor",

        "battery age": "battery_age",
        "umur battery": "battery_age",

        "health": "health_score",
        "health score": "health_score",

        "risk": "risk",
        "status": "status",

        "warranty": "warranty",

        "remaining backup": "remaining_time",
        "backup": "remaining_time"
    },

    "actions": [
        "summary",
        "count",
        "list",
        "compare",
        "analysis"
    ]
}