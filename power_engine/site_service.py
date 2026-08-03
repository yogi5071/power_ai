from Documents.power_ai.database.master_site_repository import SiteRepository


class SiteService:

    def __init__(self):
        self.repo = SiteRepository()

    def get_total_sites(self):
        return self.repo.count_sites()

    def search_site(self, keyword):
        return self.repo.search_site(keyword)

    def get_old_battery(self):
        return self.repo.get_old_battery()

    def get_warranty_expired(self):
        return self.repo.get_warranty_expired()

    def get_rectifier_obsolete(self):
        return self.repo.get_rectifier_obsolete()

    def get_lithium_statistics(self):
        return self.repo.get_lithium_statistics()

    def get_cluster_statistics(self):
        return self.repo.get_cluster_statistics()

    def get_kabupaten_statistics(self):
        return self.repo.get_kabupaten_statistics()

    def get_site_detail(self, siteid):
        return self.repo.get_site_detail(siteid)

    def close(self):
        self.repo.close()