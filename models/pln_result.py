"""
Result model for monthly PLN analysis.

Power AI Copilot

Responsibilities:
- Hold monthly PLN analysis result.
- Expose RPTAG / billing metrics.
- Expose KWHPAKAI / consumption metrics.
- Calculate monthly and overall trends.
- Preserve backward compatibility with existing PLNService
  and AIRouter consumers.

Business rules:
- NULL != 0.
- 0 is a valid recorded value.
- NULL means the monthly value is unavailable.
- KWHPAKAI and RPTAG are independent metrics.
"""

from decimal import Decimal


class PLNResult:

    def __init__(
        self,
        scope_type,
        scope_value,
        months,
        capacity=None,
        profile=None,
    ):

        self.scope_type = scope_type
        self.scope_value = scope_value

        self.months = months or []

        self.capacity = capacity or {}

        self.profile = profile or {}

    # ==========================================================
    # PROFILE
    # ==========================================================

    @property
    def siteid(self):

        return self.profile.get(
            "siteid"
        )

    @property
    def site_name(self):

        return self.profile.get(
            "site_name"
        )

    @property
    def pelanggan_id(self):

        return self.profile.get(
            "pelanggan_id"
        )

    @property
    def nama_pelanggan(self):

        return self.profile.get(
            "nama_pelanggan"
        )

    @property
    def tower_owner(self):

        return self.profile.get(
            "tower_owner"
        )

    @property
    def source_power(self):

        return self.profile.get(
            "source_power"
        )

    @property
    def amr(self):

        return self.profile.get(
            "amr"
        )

    @property
    def daya(self):

        if self.profile.get("daya") is not None:

            return self.profile.get(
                "daya"
            )

        return self.kapasitas_pln

    @property
    def jenis_inquiry(self):

        return self.profile.get(
            "jenis_inquiry"
        )

    @property
    def type_tarif(self):

        return self.profile.get(
            "type_tarif"
        )

    @property
    def schema_bayar(self):

        return self.profile.get(
            "schema_bayar"
        )

    @property
    def tp_nontp(self):

        return self.profile.get(
            "tp_nontp"
        )

    # ==========================================================
    # AVAILABLE MONTHS
    #
    # A month is considered available when either KWHPAKAI
    # or RPTAG contains a value.
    #
    # Important:
    #   0    -> available
    #   None -> unavailable
    # ==========================================================

    @property
    def available_months(self):

        return [
            month
            for month in self.months
            if (
                month.get("total_value") is not None
                or month.get("total_kwh") is not None
            )
        ]

    # ==========================================================
    # AVAILABLE BILLING MONTHS
    # ==========================================================

    @property
    def available_billing_months(self):

        return [
            month
            for month in self.months
            if month.get(
                "total_value"
            ) is not None
        ]

    # ==========================================================
    # AVAILABLE KWH MONTHS
    # ==========================================================

    @property
    def available_kwh_months(self):

        return [
            month
            for month in self.months
            if month.get(
                "total_kwh"
            ) is not None
        ]

    # ==========================================================
    # TOTAL RPTAG
    #
    # Backward compatible:
    #   total == total billing / RPTAG
    # ==========================================================

    @property
    def total(self):

        return sum(
            (
                month.get(
                    "total_value"
                ) or 0
                for month in self.available_billing_months
            ),
            0,
        )

    # ==========================================================
    # TOTAL RPTAG
    # ==========================================================

    @property
    def total_rptag(self):

        return self.total

    # ==========================================================
    # TOTAL KWH
    # ==========================================================

    @property
    def total_kwh(self):

        return sum(
            (
                month.get(
                    "total_kwh"
                ) or 0
                for month in self.available_kwh_months
            ),
            0,
        )

    # ==========================================================
    # MONTHLY AVERAGE RPTAG PER SITE
    #
    # Backward compatible:
    #   average == average_value
    # ==========================================================

    @property
    def monthly_average(self):

        values = [
            month.get(
                "average_value"
            )
            for month in self.available_billing_months
            if month.get(
                "average_value"
            ) is not None
        ]

        if not values:
            return None

        return sum(
            values
        ) / len(values)

    # ==========================================================
    # AVERAGE RPTAG
    # ==========================================================

    @property
    def average(self):

        return self.monthly_average

    # ==========================================================
    # AVERAGE KWH PER SITE
    # ==========================================================

    @property
    def average_kwh(self):

        values = [
            month.get(
                "average_kwh"
            )
            for month in self.available_kwh_months
            if month.get(
                "average_kwh"
            ) is not None
        ]

        if not values:
            return None

        return sum(
            values
        ) / len(values)

    # ==========================================================
    # AVERAGE TOTAL RPTAG PER MONTH
    # ==========================================================

    @property
    def average_total_per_month(self):

        values = [
            month.get(
                "total_value"
            )
            for month in self.available_billing_months
            if month.get(
                "total_value"
            ) is not None
        ]

        if not values:
            return None

        return sum(
            values
        ) / len(values)

    # ==========================================================
    # AVERAGE TOTAL KWH PER MONTH
    # ==========================================================

    @property
    def average_total_kwh_per_month(self):

        values = [
            month.get(
                "total_kwh"
            )
            for month in self.available_kwh_months
            if month.get(
                "total_kwh"
            ) is not None
        ]

        if not values:
            return None

        return sum(
            values
        ) / len(values)

    # ==========================================================
    # MAXIMUM RPTAG
    # ==========================================================

    @property
    def maximum(self):

        if not self.available_billing_months:
            return None

        return max(
            self.available_billing_months,
            key=lambda month: (
                month.get(
                    "total_value"
                ) or 0
            ),
        )

    # ==========================================================
    # MINIMUM RPTAG
    # ==========================================================

    @property
    def minimum(self):

        if not self.available_billing_months:
            return None

        return min(
            self.available_billing_months,
            key=lambda month: (
                month.get(
                    "total_value"
                ) or 0
            ),
        )

    # ==========================================================
    # MAXIMUM KWH
    # ==========================================================

    @property
    def maximum_kwh(self):

        if not self.available_kwh_months:
            return None

        return max(
            self.available_kwh_months,
            key=lambda month: (
                month.get(
                    "total_kwh"
                ) or 0
            ),
        )

    # ==========================================================
    # MINIMUM KWH
    # ==========================================================

    @property
    def minimum_kwh(self):

        if not self.available_kwh_months:
            return None

        return min(
            self.available_kwh_months,
            key=lambda month: (
                month.get(
                    "total_kwh"
                ) or 0
            ),
        )

    # ==========================================================
    # KAPASITAS PLN
    # ==========================================================

    @property
    def kapasitas_pln(self):

        value = self.capacity.get(
            "kapasitas_pln"
        )

        if value is not None:
            return value

        return self.profile.get(
            "daya"
        )

    # ==========================================================
    # HAS CAPACITY
    # ==========================================================

    @property
    def has_capacity(self):

        return (
            self.kapasitas_pln
            is not None
        )

    # ==========================================================
    # HAS PROFILE
    # ==========================================================

    @property
    def has_profile(self):

        return bool(
            self.profile
        )

    # ==========================================================
    # HAS DATA
    # ==========================================================

    @property
    def has_data(self):

        return bool(
            self.available_months
        )

    # ==========================================================
    # HAS BILLING DATA
    # ==========================================================

    @property
    def has_billing_data(self):

        return bool(
            self.available_billing_months
        )

    # ==========================================================
    # HAS KWH DATA
    # ==========================================================

    @property
    def has_kwh_data(self):

        return bool(
            self.available_kwh_months
        )

    # ==========================================================
    # SITE COUNT
    # ==========================================================

    @property
    def site_count(self):

        if not self.available_months:
            return 0

        return max(
            int(
                month.get(
                    "total_site"
                )
                or 0
            )
            for month in self.available_months
        )

    # ==========================================================
    # LATEST MONTH
    # ==========================================================

    @property
    def latest_month(self):

        if not self.available_months:
            return None

        return self.available_months[-1]

    # ==========================================================
    # PREVIOUS MONTH
    # ==========================================================

    @property
    def previous_month(self):

        if len(
            self.available_months
        ) < 2:

            return None

        return self.available_months[-2]

    # ==========================================================
    # LATEST RPTAG
    # ==========================================================

    @property
    def latest_rptag(self):

        month = self.latest_month

        if not month:
            return None

        return month.get(
            "total_value"
        )

    # ==========================================================
    # PREVIOUS RPTAG
    # ==========================================================

    @property
    def previous_rptag(self):

        month = self.previous_month

        if not month:
            return None

        return month.get(
            "total_value"
        )

    # ==========================================================
    # LATEST KWH
    # ==========================================================

    @property
    def latest_kwh(self):

        month = self.latest_month

        if not month:
            return None

        return month.get(
            "total_kwh"
        )

    # ==========================================================
    # PREVIOUS KWH
    # ==========================================================

    @property
    def previous_kwh(self):

        month = self.previous_month

        if not month:
            return None

        return month.get(
            "total_kwh"
        )

    # ==========================================================
    # LATEST AVERAGE RPTAG
    # ==========================================================

    @property
    def latest_average(self):

        month = self.latest_month

        if not month:
            return None

        return month.get(
            "average_value"
        )

    # ==========================================================
    # PREVIOUS AVERAGE RPTAG
    # ==========================================================

    @property
    def previous_average(self):

        month = self.previous_month

        if not month:
            return None

        return month.get(
            "average_value"
        )

    # ==========================================================
    # LATEST AVERAGE KWH
    # ==========================================================

    @property
    def latest_average_kwh(self):

        month = self.latest_month

        if not month:
            return None

        return month.get(
            "average_kwh"
        )

    # ==========================================================
    # PREVIOUS AVERAGE KWH
    # ==========================================================

    @property
    def previous_average_kwh(self):

        month = self.previous_month

        if not month:
            return None

        return month.get(
            "average_kwh"
        )

    # ==========================================================
    # RPTAG CHANGE ABSOLUTE
    #
    # Backward compatible alias:
    #   average_change
    # ==========================================================

    @property
    def average_change(self):

        latest = self.latest_average
        previous = self.previous_average

        if (
            latest is None
            or previous is None
        ):
            return None

        return latest - previous

    @property
    def rptag_change(self):

        return self.average_change

    # ==========================================================
    # RPTAG CHANGE PERCENTAGE
    # ==========================================================

    @property
    def average_change_percentage(self):

        latest = self.latest_average
        previous = self.previous_average

        if (
            latest is None
            or previous is None
            or previous == 0
        ):
            return None

        return (
            (
                latest - previous
            )
            / previous
        ) * 100

    @property
    def rptag_change_percentage(self):

        return self.average_change_percentage

    # ==========================================================
    # KWH CHANGE ABSOLUTE
    # ==========================================================

    @property
    def kwh_change(self):

        latest = self.latest_average_kwh
        previous = self.previous_average_kwh

        if (
            latest is None
            or previous is None
        ):
            return None

        return latest - previous

    # ==========================================================
    # KWH CHANGE PERCENTAGE
    # ==========================================================

    @property
    def kwh_change_percentage(self):

        latest = self.latest_average_kwh
        previous = self.previous_average_kwh

        if (
            latest is None
            or previous is None
            or previous == 0
        ):
            return None

        return (
            (
                latest - previous
            )
            / previous
        ) * 100

    # ==========================================================
    # RPTAG TREND CHANGES
    #
    # Existing trend behavior is preserved.
    # ==========================================================

    @property
    def trend_changes(self):

        months = (
            self.available_billing_months
        )

        if len(months) < 2:
            return []

        changes = []

        for index in range(
            1,
            len(months)
        ):

            previous = months[
                index - 1
            ]

            current = months[
                index
            ]

            previous_average = (
                previous.get(
                    "average_value"
                )
            )

            current_average = (
                current.get(
                    "average_value"
                )
            )

            if (
                previous_average is None
                or current_average is None
            ):
                continue

            absolute_change = (
                current_average
                - previous_average
            )

            if absolute_change > 0:

                direction = "naik"

            elif absolute_change < 0:

                direction = "turun"

            else:

                direction = "tetap"

            if previous_average == 0:

                percentage_change = None

            else:

                percentage_change = (
                    absolute_change
                    / previous_average
                ) * 100

            changes.append(
                {
                    "from": previous,
                    "to": current,
                    "from_average": (
                        previous_average
                    ),
                    "to_average": (
                        current_average
                    ),
                    "absolute_change": (
                        absolute_change
                    ),
                    "percentage_change": (
                        percentage_change
                    ),
                    "direction": direction,
                }
            )

        return changes

    # ==========================================================
    # KWH TREND CHANGES
    # ==========================================================

    @property
    def kwh_trend_changes(self):

        months = (
            self.available_kwh_months
        )

        if len(months) < 2:
            return []

        changes = []

        for index in range(
            1,
            len(months)
        ):

            previous = months[
                index - 1
            ]

            current = months[
                index
            ]

            previous_average = (
                previous.get(
                    "average_kwh"
                )
            )

            current_average = (
                current.get(
                    "average_kwh"
                )
            )

            if (
                previous_average is None
                or current_average is None
            ):
                continue

            absolute_change = (
                current_average
                - previous_average
            )

            if absolute_change > 0:

                direction = "naik"

            elif absolute_change < 0:

                direction = "turun"

            else:

                direction = "tetap"

            if previous_average == 0:

                percentage_change = None

            else:

                percentage_change = (
                    absolute_change
                    / previous_average
                ) * 100

            changes.append(
                {
                    "from": previous,
                    "to": current,
                    "from_average": (
                        previous_average
                    ),
                    "to_average": (
                        current_average
                    ),
                    "absolute_change": (
                        absolute_change
                    ),
                    "percentage_change": (
                        percentage_change
                    ),
                    "direction": direction,
                }
            )

        return changes

    # ==========================================================
    # TREND DIRECTION
    # ==========================================================

    @property
    def trend_direction(self):

        changes = self.trend_changes

        if not changes:
            return []

        return [
            change[
                "direction"
            ]
            for change in changes
        ]

    # ==========================================================
    # KWH TREND DIRECTION
    # ==========================================================

    @property
    def kwh_trend_direction(self):

        changes = (
            self.kwh_trend_changes
        )

        if not changes:
            return []

        return [
            change[
                "direction"
            ]
            for change in changes
        ]

    # ==========================================================
    # TREND LABEL
    # ==========================================================

    @property
    def trend_label(self):

        directions = (
            self.trend_direction
        )

        if not directions:
            return None

        return " → ".join(
            directions
        )

    # ==========================================================
    # KWH TREND LABEL
    # ==========================================================

    @property
    def kwh_trend_label(self):

        directions = (
            self.kwh_trend_direction
        )

        if not directions:
            return None

        return " → ".join(
            directions
        )

    # ==========================================================
    # OVERALL RPTAG TREND
    #
    # First available billing month
    # compared with last available billing month.
    # ==========================================================

    @property
    def overall_trend(self):

        months = (
            self.available_billing_months
        )

        if len(months) < 2:
            return None

        first = months[0]
        last = months[-1]

        first_average = (
            first.get(
                "average_value"
            )
        )

        last_average = (
            last.get(
                "average_value"
            )
        )

        if (
            first_average is None
            or last_average is None
        ):
            return None

        if last_average > first_average:

            return "naik"

        if last_average < first_average:

            return "turun"

        return "tetap"

    # ==========================================================
    # OVERALL KWH TREND
    # ==========================================================

    @property
    def overall_kwh_trend(self):

        months = (
            self.available_kwh_months
        )

        if len(months) < 2:
            return None

        first = months[0]
        last = months[-1]

        first_average = (
            first.get(
                "average_kwh"
            )
        )

        last_average = (
            last.get(
                "average_kwh"
            )
        )

        if (
            first_average is None
            or last_average is None
        ):
            return None

        if last_average > first_average:

            return "naik"

        if last_average < first_average:

            return "turun"

        return "tetap"

    # ==========================================================
    # OVERALL RPTAG CHANGE
    # ==========================================================

    @property
    def overall_change(self):

        months = (
            self.available_billing_months
        )

        if len(months) < 2:
            return None

        first_average = (
            months[0].get(
                "average_value"
            )
        )

        last_average = (
            months[-1].get(
                "average_value"
            )
        )

        if (
            first_average is None
            or last_average is None
        ):
            return None

        return (
            last_average
            - first_average
        )

    # ==========================================================
    # OVERALL KWH CHANGE
    # ==========================================================

    @property
    def overall_kwh_change(self):

        months = (
            self.available_kwh_months
        )

        if len(months) < 2:
            return None

        first_average = (
            months[0].get(
                "average_kwh"
            )
        )

        last_average = (
            months[-1].get(
                "average_kwh"
            )
        )

        if (
            first_average is None
            or last_average is None
        ):
            return None

        return (
            last_average
            - first_average
        )

    # ==========================================================
    # OVERALL RPTAG CHANGE PERCENTAGE
    # ==========================================================

    @property
    def overall_change_percentage(self):

        months = (
            self.available_billing_months
        )

        if len(months) < 2:
            return None

        first_average = (
            months[0].get(
                "average_value"
            )
        )

        last_average = (
            months[-1].get(
                "average_value"
            )
        )

        if (
            first_average is None
            or last_average is None
            or first_average == 0
        ):
            return None

        return (
            (
                last_average
                - first_average
            )
            / first_average
        ) * 100

    # ==========================================================
    # OVERALL KWH CHANGE PERCENTAGE
    # ==========================================================

    @property
    def overall_kwh_change_percentage(self):

        months = (
            self.available_kwh_months
        )

        if len(months) < 2:
            return None

        first_average = (
            months[0].get(
                "average_kwh"
            )
        )

        last_average = (
            months[-1].get(
                "average_kwh"
            )
        )

        if (
            first_average is None
            or last_average is None
            or first_average == 0
        ):
            return None

        return (
            (
                last_average
                - first_average
            )
            / first_average
        ) * 100

    # ==========================================================
    # HAS TREND
    # ==========================================================

    @property
    def has_trend(self):

        return (
            len(
                self.available_billing_months
            ) >= 2
        )

    # ==========================================================
    # HAS KWH TREND
    # ==========================================================

    @property
    def has_kwh_trend(self):

        return (
            len(
                self.available_kwh_months
            ) >= 2
        )

    # ==========================================================
    # HAS MULTI PERIOD TREND
    # ==========================================================

    @property
    def has_multi_period_trend(self):

        return (
            len(
                self.available_billing_months
            ) >= 3
        )

    # ==========================================================
    # HAS MULTI PERIOD KWH TREND
    # ==========================================================

    @property
    def has_multi_period_kwh_trend(self):

        return (
            len(
                self.available_kwh_months
            ) >= 3
        )