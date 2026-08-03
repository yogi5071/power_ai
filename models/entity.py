"""
Entity Model
Power AI Copilot
"""


class Entity:

    def __init__(self):

        # Site
        self.site_id = None

        # Area
        self.city = None
        self.cluster = None
        self.region = None

        # Equipment
        self.vendor = None
        self.technology = None

        # Alarm
        self.alarm = None

        # Battery
        self.battery_status = None

        # Intent Helper
        self.site_name = None
        self.keyword = None

    @property
    def has_site(self):
        return self.site_id is not None

    @property
    def has_area(self):
        return (
            self.city is not None or
            self.cluster is not None or
            self.region is not None
        )