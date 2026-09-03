from power_engine.master_site_query_service import MasterSiteQueryService


class FakeRepository:
    def get_distinct_values(self, field_name):
        return {
            "kabupaten": ["Sidoarjo"],
            "kecamatan": [],
            "cluster": ["Cluster A"],
            "nop": [],
            "kategori_umur": [],
            "status_warranty": [],
            "kategori_rectifier": [],
        }[field_name]

    def query_aggregate(self, **kwargs):
        assert kwargs["operation"] == "sum"
        assert kwargs["metric_field"] == "total_vrla"
        assert ("jenis_battery", "VRLA") in kwargs["filters"]
        assert ("kabupaten", "Sidoarjo") in kwargs["filters"]
        return [{"value": 42}]


def test_total_vrla_in_kabupaten_is_deterministic():
    service = MasterSiteQueryService(FakeRepository())

    answer = service.execute(
        "Berapa jumlah seluruh battery VRLA di Kabupaten Sidoarjo?"
    )

    assert answer == "Total unit VRLA untuk Jenis Battery VRLA, Kabupaten Sidoarjo: 42"
