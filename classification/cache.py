class ClassificationCache:

    def __init__(self):

        self.site = set()

        self.kabupaten = set()

        self.kecamatan = set()

        self.cluster = set()

        self.nop = set()

    def clear(self):

        self.site.clear()

        self.kabupaten.clear()

        self.kecamatan.clear()

        self.cluster.clear()

        self.nop.clear()