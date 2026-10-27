class ReportGenerator:

    @staticmethod
    def generate(result):

        if result is None:
            return "Site tidak ditemukan."

        site = result.site

        report = f"""
============================================================
                    POWER AI COPILOT
============================================================

AI SUMMARY
------------------------------------------------------------
Battery {site.battery} berumur {result.battery_age} tahun
dengan Health Score {result.health_score}/100.

Status saat ini adalah {result.status}
dengan Risk Level {result.risk}.

------------------------------------------------------------

GENERAL INFORMATION

Site ID          : {site.siteid}
Site Name        : {site.site_name}

Cluster          : {site.cluster}
Kabupaten        : {site.kabupaten}
Kecamatan        : {site.kecamatan}

Longitude        : {site.longitude}
Latitude         : {site.latitude}

------------------------------------------------------------

BATTERY INFORMATION

Battery Type     : {site.battery}

Battery Age      : {result.battery_age} Tahun

Technology       : {result.technology}

Warranty         : {result.warranty}

Total Bank       : {site.total_bank}

Rectifier Load   : {site.total_load_rectifier} A

Remaining Time   : {result.remaining_time} Minutes

------------------------------------------------------------

ANALYSIS

Health Score     : {result.health_score}/100

Status           : {result.status}

Risk Level       : {result.risk}

------------------------------------------------------------

RECOMMENDATION

{result.recommendation}

============================================================
"""

        return report