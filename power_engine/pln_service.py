"""PLN monthly analysis service."""

from datetime import date

from database.site_pln_monthly_repository import SitePLNMonthlyRepository
from models.pln_result import PLNResult


class PLNService:

    def __init__(self):

        self.repository = SitePLNMonthlyRepository()

    # ==========================================================
    # MONTH PERIODS
    # ==========================================================

    @staticmethod
    def month_periods(months: int, today=None):

        today = today or date.today()

        months = max(
            1,
            min(int(months), 12)
        )

        result = []

        year = today.year
        month = today.month

        for _ in range(months):

            result.append(
                (year, month)
            )

            month -= 1

            if month == 0:

                month = 12
                year -= 1

        result.reverse()

        return result

    # ==========================================================
    # NORMALIZE SCOPE
    #
    # EntityExtractor:
    #
    # province -> Jawa Timur
    #
    # Repository:
    #
    # union -> seluruh data
    #
    # PLNResult tetap menggunakan scope asli.
    # ==========================================================

    @staticmethod
    def _repository_scope(scope_type):

        if scope_type == "province":
            return "union"

        return scope_type

    # ==========================================================
    # ANALYZE
    #
    # Menghasilkan:
    #
    # - Monthly KWHPAKAI
    # - Monthly RPTAG
    # - Trend KWH
    # - Trend RPTAG
    # - Capacity untuk site
    # - Site profile untuk site
    #
    # IMPORTANT:
    #
    # Profile hanya relevan untuk scope siteid.
    #
    # Untuk province / kabupaten / kecamatan / nop / cluster
    # profile tidak diambil karena scope dapat mencakup banyak site.
    # ==========================================================

    def analyze(
        self,
        scope_type,
        scope_value,
        months=1
    ):

        # ------------------------------------------------------
        # NORMALIZE INPUT
        # ------------------------------------------------------

        scope_type = (
            str(scope_type).strip().lower()
            if scope_type
            else None
        )

        scope_value = (
            str(scope_value).strip()
            if scope_value
            else None
        )

        # ------------------------------------------------------
        # VALIDATE SCOPE
        # ------------------------------------------------------

        if not scope_type:
            return None

        if not scope_value:
            return None

        # ------------------------------------------------------
        # PERIOD
        # ------------------------------------------------------

        periods = self.month_periods(
            months
        )

        # ------------------------------------------------------
        # REPOSITORY SCOPE
        #
        # province -> union
        #
        # siteid / kecamatan / kabupaten / nop / cluster
        # diteruskan apa adanya.
        # ------------------------------------------------------

        repository_scope = self._repository_scope(
            scope_type
        )

        # ======================================================
        # MONTHLY PLN
        #
        # Repository sekarang mengembalikan:
        #
        # total_kwh
        # average_kwh
        # minimum_kwh
        # maximum_kwh
        #
        # total_value / RPTAG
        # average_value
        # minimum_value
        # maximum_value
        # ======================================================

        rows = self.repository.get_months(
            repository_scope,
            scope_value,
            periods
        )

        # ======================================================
        # CAPACITY
        #
        # Kapasitas PLN adalah kapasitas PER SITE.
        #
        # Tidak diagregasikan untuk:
        #
        # province
        # kabupaten
        # kecamatan
        # nop
        # cluster
        # ======================================================

        capacity = {}

        if scope_type == "siteid":

            capacity = (
                self.repository.get_site_capacity(
                    scope_value,
                    date.today().year
                )
                or {}
            )

        # ======================================================
        # SITE PROFILE
        #
        # Profile hanya diambil untuk scope siteid.
        #
        # Data:
        #
        # pelanggan_id
        # nama_pelanggan
        # tower_owner
        # source_power
        # amr
        # daya
        # jenis_inquiry
        # type_tarif
        # schema_bayar
        # tp_nontp
        #
        # Contoh:
        #
        # BDO002
        # ------------------------------------------------------
        # pelanggan_id   : ...
        # nama_pelanggan : TELKOMSEL
        # source_power   : PLN
        # amr            : AMR
        # daya           : 23000
        # jenis_inquiry  : TPPOSTPAID
        # type_tarif     : B2
        # schema_bayar   : SENTRALISASI
        # tp_nontp       : TP
        # ======================================================

        profile = {}

        if scope_type == "siteid":

            profile = (
                self.repository.get_site_profile(
                    scope_value,
                    date.today().year
                )
                or {}
            )

        # ======================================================
        # RESULT
        #
        # Scope type yang diberikan ke PLNResult tetap scope asli.
        #
        # province:
        #
        #   User scope      = province
        #   Repository      = union
        #   PLNResult       = province
        #
        # siteid:
        #
        #   User scope      = siteid
        #   Repository      = siteid
        #   PLNResult       = siteid
        #
        # Profile hanya terisi pada siteid.
        # ======================================================

        result = PLNResult(
            scope_type,
            scope_value,
            rows,
            capacity,
            profile
        )

        # ======================================================
        # SITE PROFILE FALLBACK
        #
        # Untuk pertanyaan kondisi/profile site, data profile
        # tetap valid walaupun bulan berjalan belum memiliki
        # KWH/RPTAG. Contoh pada 1 September 2026:
        # September dapat NULL sementara Januari-Agustus sudah ada.
        #
        # Jika scope siteid dan periode berjalan kosong, gunakan
        # bulan terakhir yang memiliki data monthly agar PLNResult
        # tetap dapat menyajikan profile + latest available billing.
        # ======================================================

        if (
            scope_type == "siteid"
            and not result.available_months
            and profile
        ):

            raw_site = (
                self.repository.get_site_data(
                    scope_value,
                    date.today().year
                )
                or {}
            )

            fallback_rows = []

            for month in range(12, 0, -1):

                kwh_key = f"kwh_{self.repository.MONTH_NAMES[month].lower()}"
                rptag_key = f"rptag_{self.repository.MONTH_NAMES[month].lower()}"

                kwh = raw_site.get(kwh_key)
                rptag = raw_site.get(rptag_key)

                if kwh is None and rptag is None:
                    continue

                fallback_rows.append(
                    {
                        "year": date.today().year,
                        "month": month,
                        "month_name": self.repository.MONTH_NAMES[month],
                        "total_site": 1,
                        "total_kwh": kwh,
                        "total_value": rptag,
                        "average_kwh": kwh,
                        "average_value": rptag,
                        "minimum_kwh": kwh,
                        "maximum_kwh": kwh,
                        "minimum_value": rptag,
                        "maximum_value": rptag,
                    }
                )

                break

            if fallback_rows:

                result = PLNResult(
                    scope_type,
                    scope_value,
                    fallback_rows,
                    capacity,
                    profile
                )

        # ======================================================
        # NO DATA
        #
        # Jangan menganggap nilai 0 sebagai no-data.
        #
        # 0:
        #   data tersedia dan nilainya memang nol.
        #
        # None:
        #   data tidak tersedia.
        # ======================================================

        if not result.available_months:

            return None

        return result

    # ==========================================================
    # SITE PROFILE
    #
    # Convenience method untuk mengambil struktur PLN sebuah
    # site tanpa melakukan analisis aggregate.
    #
    # Contoh:
    #
    # service.get_site_profile("BDO002")
    #
    # ==========================================================

    def get_site_profile(
        self,
        siteid,
        tahun=None,
    ):

        siteid = (
            str(siteid).strip()
            if siteid
            else None
        )

        if not siteid:
            return None

        if tahun is None:

            tahun = date.today().year

        return (
            self.repository.get_site_profile(
                siteid,
                tahun
            )
            or None
        )

    # ==========================================================
    # COMPLETE SITE DATA
    #
    # Mengambil:
    #
    # - Profile PLN
    # - Historical KWHPAKAI
    # - Historical RPTAG
    #
    # Tanpa mengubah data mentah.
    # ==========================================================

    def get_site_data(
        self,
        siteid,
        tahun=None,
    ):

        siteid = (
            str(siteid).strip()
            if siteid
            else None
        )

        if not siteid:
            return None

        if tahun is None:

            tahun = date.today().year

        return (
            self.repository.get_site_data(
                siteid,
                tahun
            )
            or None
        )

    # ==========================================================
    # SITE ANALYSIS
    #
    # Convenience wrapper untuk site-level analysis.
    #
    # Contoh:
    #
    # service.analyze_site("BDO002", 3)
    #
    # Hasil:
    #
    # PLNResult
    #   ├── profile
    #   ├── capacity
    #   └── months
    #       ├── KWH
    #       └── RPTAG
    # ==========================================================

    def analyze_site(
        self,
        siteid,
        months=1,
    ):

        siteid = (
            str(siteid).strip()
            if siteid
            else None
        )

        if not siteid:
            return None

        return self.analyze(
            "siteid",
            siteid,
            months
        )

    # ==========================================================
    # PLN SCOPE ANALYSIS
    #
    # Convenience wrappers.
    # ==========================================================

    def analyze_province(
        self,
        province="Jawa Timur",
        months=1,
    ):

        return self.analyze(
            "province",
            province,
            months
        )

    def analyze_kabupaten(
        self,
        kabupaten,
        months=1,
    ):

        return self.analyze(
            "kabupaten",
            kabupaten,
            months
        )

    def analyze_kecamatan(
        self,
        kecamatan,
        months=1,
    ):

        return self.analyze(
            "kecamatan",
            kecamatan,
            months
        )

    def analyze_nop(
        self,
        nop,
        months=1,
    ):

        return self.analyze(
            "nop",
            nop,
            months
        )

    def analyze_cluster(
        self,
        cluster,
        months=1,
    ):

        return self.analyze(
            "cluster",
            cluster,
            months
        )