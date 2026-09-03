"""Entity Model
Power AI Copilot
"""


class Entity:

    def __init__(self):

        self.site_id = None

        self.city = None
        self.cluster = None
        self.region = None
        self.kecamatan = None
        self.kabupaten = None
        self.nop = None

        self.vendor = None
        self.technology = None

        self.alarm = None

        self.battery_status = None

        self.site_name = None
        self.keyword = None

        # Operational query context
        self.scope_type = None
        self.scope_value = None
        self.period_months = None

    @property
    def has_site(self):
        return self.site_id is not None

    @property
    def has_area(self):
        return any(
            value is not None
            for value in (
                self.city,
                self.cluster,
                self.region,
                self.kecamatan,
                self.kabupaten,
                self.nop,
            )
        )
