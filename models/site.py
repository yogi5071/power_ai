from datetime import date, datetime


class Site:

    def __init__(self, row):
        self.siteid = row.get("siteid")
        self.site_name = row.get("site_name")
        self.cluster = row.get("cluster")
        self.kabupaten = row.get("kabupaten")
        self.kecamatan = row.get("kecamatan")
        self.nop_name = row.get("nop_name")
        self.longitude = row.get("longitude")
        self.latitude = row.get("latitude")
        self.battery = row.get("battery")
        self.total_bank = row.get("total_bank", 0)
        self.total_load_rectifier = row.get("total_load_rectifier_a") or 0
        self.kategori_rectifier = row.get("kategori_rectifier")
        self.install_date = row.get("tgl_instalasi_battery")
        self.status_warranty_battery = row.get("status_warranty_battery")

        # Engineering-derived outage context.
        self.pemadaman_min = row.get("pemadaman_min")
        self.pemadaman_avg = row.get("pemadaman_avg")
        self.pemadaman_max = row.get("pemadaman_max")

    @property
    def site_id(self):
        return self.siteid

    @property
    def is_vrla(self):
        return (self.battery or "").strip().upper() == "VRLA"

    @property
    def is_lithium(self):
        return (self.battery or "").strip().upper() == "LITHIUM"

    @property
    def battery_age(self):
        if self.install_date is None:
            return 0
        install = self.install_date
        if isinstance(install, str):
            try:
                install = datetime.strptime(install, "%Y-%m-%d").date()
            except Exception:
                return 0
        elif isinstance(install, datetime):
            install = install.date()
        today = date.today()
        age = today.year - install.year
        if (today.month, today.day) < (install.month, install.day):
            age -= 1
        return max(age, 0)
