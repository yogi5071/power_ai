"""
Intent Detector
Power AI Copilot
"""


class IntentDetector:
    """
    Deterministic intent detection for the Power AI operational domains.

    Prinsip:
    - Intent ditentukan secara deterministik.
    - PLN harus tetap terdeteksi walaupun user tidak menyebut
      kata "PLN" secara eksplisit.
    - Kata seperti "tagihan", "rekening", "biaya listrik",
      "KWH", dan "RPTAG" dianggap sebagai indikasi PLN.
    - Rectifier memiliki intent khusus agar tidak salah masuk
      ke domain alarm.
    """

    # ==========================================================
    # BATTERY
    # ==========================================================

    BATTERY_KEYWORDS = (
        "battery",
        "baterai",
        "battery health",
        "backup",
        "backup time",
        "health score",
        "vrla",
        "lithium",
    )

    # ==========================================================
    # OUTAGE
    # ==========================================================

    OUTAGE_KEYWORDS = (
        "pemadaman",
        "padam",
        "mati listrik",
        "listrik mati",
        "outage",
        "blackout",
    )

    # ==========================================================
    # PLN
    # ==========================================================

    PLN_KEYWORDS = (
        # ------------------------------------------------------
        # IDENTITAS PLN
        # ------------------------------------------------------

        "pln",

        # ------------------------------------------------------
        # TAGIHAN / PEMBAYARAN
        # ------------------------------------------------------

        "tagihan pln",
        "tagihan",
        "biaya pln",
        "biaya listrik",
        "rekening listrik",
        "rekening pln",
        "tagihan listrik",
        "bayar listrik",
        "pembayaran listrik",
        "penagihan",

        # ------------------------------------------------------
        # KONSUMSI / PEMAKAIAN
        # ------------------------------------------------------

        "konsumsi listrik",
        "pemakaian listrik",

        # ------------------------------------------------------
        # KWH
        #
        # KWH merupakan field utama pada data PLN.
        #
        # Contoh:
        #
        # "site mana kwh di atas 5000"
        # "berapa site dengan kwh > 5000"
        # "kwh tertinggi"
        # "kwh terendah"
        # ------------------------------------------------------

        "kwh",
        "kwh pakai",
        "kwh pemakaian",
        "pemakaian kwh",
        "konsumsi kwh",

        # ------------------------------------------------------
        # RPTAG
        #
        # RPTAG merupakan nilai tagihan PLN.
        #
        # Contoh:
        #
        # "site mana rptag di bawah 1 juta"
        # "rptag tertinggi"
        # "rptag terendah"
        # ------------------------------------------------------

        "rptag",
        "rp tag",
        "nilai tagihan",
        "nominal tagihan",

        # ------------------------------------------------------
        # KAPASITAS / DAYA
        # ------------------------------------------------------

        "kapasitas pln",
        "daya pln",
        "kapasitas listrik",
        "daya listrik",
        "tarif listrik",
        "tarif",
        "tower owner",
        "jenis inquiry",
        "schema bayar",
        "schema pembayaran",
        "customer",

        # ------------------------------------------------------
        # INFORMASI PELANGGAN PLN
        # ------------------------------------------------------

        "pelanggan pln",
        "id pelanggan",
        "nomor pelanggan",
        "nomor registrasi pln",
        "registrasi pln",
    )

    # ==========================================================
    # AMR
    # ==========================================================

    AMR_KEYWORDS = (
        "amr",
        "belum amr",
        "sudah amr",
        "site amr",
        "status amr",
        "informasi amr",
        "meter amr",
        "metering amr",
    )

    # ==========================================================
    # RECTIFIER
    #
    # Rectifier menjadi DOMAIN tersendiri.
    #
    # Tujuannya:
    #
    # "Bagaimana kondisi rectifier Jawa Timur?"
    # "Berapa rectifier obsolete Jawa Timur?"
    # "Berapa site rectifier obsolete Sidoarjo?"
    #
    # tidak masuk ke intent alarm.
    # ==========================================================

    RECTIFIER_KEYWORDS = (
        "rectifier",
        "recti",
        "rectifier obsolete",
        "rectifier non obsolete",
        "non obsolete rectifier",
        "obsolete rectifier",
        "kategori rectifier",
        "jumlah rectifier",
        "total rectifier",
        "unit rectifier",
    )

    # ==========================================================
    # ALARM
    #
    # "rectifier" DIHAPUS dari sini.
    #
    # Karena rectifier sekarang memiliki domain sendiri.
    # ==========================================================

    ALARM_KEYWORDS = (
        "alarm",
        "mains fail",
        "genset",
        "module fail",
    )

    # ==========================================================
    # AREA
    # ==========================================================

    AREA_KEYWORDS = (
        "surabaya",
        "malang",
        "sidoarjo",
        "gresik",
        "cluster",
        "kabupaten",
        "kecamatan",
        "wilayah",
        "area",
    )

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    DASHBOARD_KEYWORDS = (
        "summary",
        "dashboard",
        "statistik",
        "trend",
        "grafik",
    )

    # ==========================================================
    # DETECT
    # ==========================================================

    @classmethod
    def detect(cls, message: str):

        text = (
            message or ""
        ).lower().strip()

        # ======================================================
        # DETECTION FLAGS
        # ======================================================

        has_battery = any(
            keyword in text
            for keyword in cls.BATTERY_KEYWORDS
        )

        has_outage = any(
            keyword in text
            for keyword in cls.OUTAGE_KEYWORDS
        )

        has_pln = any(
            keyword in text
            for keyword in cls.PLN_KEYWORDS
        )

        has_amr = any(
            keyword in text
            for keyword in cls.AMR_KEYWORDS
        )

        has_rectifier = any(
            keyword in text
            for keyword in cls.RECTIFIER_KEYWORDS
        )

        has_alarm = any(
            keyword in text
            for keyword in cls.ALARM_KEYWORDS
        )

        has_dashboard = any(
            keyword in text
            for keyword in cls.DASHBOARD_KEYWORDS
        )

        has_area = any(
            keyword in text
            for keyword in cls.AREA_KEYWORDS
        )

        # ======================================================
        # COMBINED INTENT
        # ======================================================

        if has_battery and has_outage:
            return "battery_outage"

        # ======================================================
        # AMR
        # ======================================================

        # "AMR PLN site ..." is a PLN profile question.  Keep plain AMR
        # operational questions on the AMR route, but do not let AMR shadow
        # a deterministic PLN lookup.
        if has_amr and not has_pln:
            return "amr"

        # ======================================================
        # PLN
        #
        # Contoh:
        #
        # "berapa tagihan SBY064"
        # "tagihan SBY064 4 bulan kebelakang"
        # "bagaimana kondisi PLN Jawa Timur"
        # "site mana kwh di atas 5000"
        # "berapa site rptag di bawah 1000000"
        # ======================================================

        if has_pln:
            return "pln"

        # ======================================================
        # RECTIFIER
        #
        # Harus sebelum ALARM.
        # ======================================================

        if has_rectifier:
            return "rectifier"

        # ======================================================
        # OUTAGE
        # ======================================================

        if has_outage:
            return "outage"

        # ======================================================
        # BATTERY
        # ======================================================

        if has_battery:
            return "battery"

        # ======================================================
        # ALARM
        # ======================================================

        if has_alarm:
            return "alarm"

        # ======================================================
        # DASHBOARD
        # ======================================================

        if has_dashboard:
            return "dashboard"

        # ======================================================
        # AREA
        # ======================================================

        if has_area:
            return "area"

        # ======================================================
        # GENERAL
        # ======================================================

        return "general"
