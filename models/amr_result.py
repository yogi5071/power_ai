"""Result model for AMR analysis."""


class AMRResult:

    def __init__(
        self,
        scope_type,
        scope_value,
        statistics,
        sites=None,
    ):

        self.scope_type = scope_type
        self.scope_value = scope_value

        statistics = statistics or {}

        self.total_site = int(
            statistics.get("total_site") or 0
        )

        self.total_amr = int(
            statistics.get("total_amr") or 0
        )

        self.total_belum_amr = int(
            statistics.get("total_belum_amr") or 0
        )

        self.total_unknown = int(
            statistics.get("total_unknown") or 0
        )

        self.sites = sites or []

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @property
    def is_valid(self):

        return (
            self.total_site
            == self.total_amr
            + self.total_belum_amr
            + self.total_unknown
        )

    # ==========================================================
    # PERCENTAGE
    # ==========================================================

    @property
    def amr_percentage(self):

        if self.total_site == 0:
            return 0

        return (
            self.total_amr
            / self.total_site
        ) * 100

    @property
    def belum_amr_percentage(self):

        if self.total_site == 0:
            return 0

        return (
            self.total_belum_amr
            / self.total_site
        ) * 100

    @property
    def unknown_percentage(self):

        if self.total_site == 0:
            return 0

        return (
            self.total_unknown
            / self.total_site
        ) * 100

    # ==========================================================
    # HAS DATA
    # ==========================================================

    @property
    def has_data(self):

        return self.total_site > 0