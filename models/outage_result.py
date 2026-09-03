"""Result model for engineering outage analysis."""


class OutageResult:
    def __init__(self, scope_type, scope_value, row):
        self.scope_type = scope_type
        self.scope_value = scope_value

        self.total_site = int(row.get("total_site") or 0)

        self.average = row.get("outage_avg")
        self.maximum = row.get("outage_max")

    @property
    def has_data(self):
        return (
            self.total_site > 0
            and self.average is not None
        )