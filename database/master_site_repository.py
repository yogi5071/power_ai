from database.base_repository import BaseRepository
from models.site import Site


class SiteRepository(BaseRepository):

    # =====================================================
    # TOTAL SITE
    # =====================================================

    def count_sites(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM master_site
        """)

        row = cursor.fetchone()

        cursor.close()

        return row["total"]

    # =====================================================
    # SEARCH SITE
    # =====================================================

    def search_site(self, keyword):

        cursor = self.get_cursor()

        sql = """
            SELECT
                siteid,
                site_name,
                cluster,
                kabupaten,
                kecamatan,
                longitude,
                latitude,
                battery,
                total_bank,
                total_load_rectifier_a,
                kategori_rectifier,
                tgl_instalasi_battery,
                status_warranty_battery
            FROM master_site
            WHERE
                siteid LIKE %s
                OR site_name LIKE %s
                OR cluster LIKE %s
                OR kabupaten LIKE %s
                OR kecamatan LIKE %s
            ORDER BY site_name
            LIMIT 20
        """

        like = f"%{keyword}%"

        cursor.execute(sql, (like, like, like, like, like))

        rows = cursor.fetchall()

        cursor.close()

        return [Site(row) for row in rows]

    # =====================================================
    # DETAIL SITE
    # =====================================================

    def get_site_detail(self, siteid):

        cursor = self.get_cursor()

        sql = """
            SELECT
                siteid,
                site_name,
                cluster,
                kabupaten,
                kecamatan,
                longitude,
                latitude,
                battery,
                total_bank,
                total_load_rectifier_a,
                kategori_rectifier,
                tgl_instalasi_battery,
                status_warranty_battery
            FROM master_site
            WHERE siteid=%s
        """

        cursor.execute(sql, (siteid,))

        row = cursor.fetchone()

        cursor.close()

        if row is None:
            return None

        return Site(row)

    # =====================================================
    # OLD BATTERY
    # =====================================================

    def get_old_battery(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                siteid,
                site_name,
                cluster,
                kabupaten,
                kecamatan,
                longitude,
                latitude,
                battery,
                total_bank,
                total_load_rectifier_a,
                kategori_rectifier,
                tgl_instalasi_battery,
                status_warranty_battery
            FROM master_site
        """)

        rows = cursor.fetchall()

        cursor.close()

        sites = [Site(row) for row in rows]

        return [site for site in sites if site.battery_age > 1]

    # =====================================================
    # WARRANTY EXPIRED
    # =====================================================

    def get_warranty_expired(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                siteid,
                site_name,
                status_warranty_battery
            FROM master_site
            WHERE status_warranty_battery='Expired'
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows

    # =====================================================
    # RECTIFIER OBSOLETE
    # =====================================================

    def get_rectifier_obsolete(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                siteid,
                site_name,
                jumlah_rectifier_obsolete
            FROM master_site
            WHERE jumlah_rectifier_obsolete > 0
            ORDER BY jumlah_rectifier_obsolete DESC
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows

    # =====================================================
    # LITHIUM STATISTIC
    # =====================================================

    def get_lithium_statistics(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                SUM(total_lithium) AS total_lithium,
                SUM(total_vrla) AS total_vrla
            FROM master_site
        """)

        row = cursor.fetchone()

        cursor.close()

        return row

    # =====================================================
    # CLUSTER STATISTIC
    # =====================================================

    def get_cluster_statistics(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                cluster,
                COUNT(*) AS total_site
            FROM master_site
            GROUP BY cluster
            ORDER BY total_site DESC
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows

    # =====================================================
    # KABUPATEN STATISTIC
    # =====================================================

    def get_kabupaten_statistics(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                kabupaten,
                COUNT(*) AS total_site
            FROM master_site
            GROUP BY kabupaten
            ORDER BY total_site DESC
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows