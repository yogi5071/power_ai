from types import SimpleNamespace

from power_engine.ai.ai_router import AIRouter
from power_engine.ai.intent_detector import IntentDetector
from power_engine.ai.gemini_service import GeminiService
import power_engine.ai.ai_router as router_module
import power_engine.ai.gemini_service as gemini_module


class FakeRepository:
    MONTH_NAMES = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember",
    }

    def get_months(self, scope, value, periods):
        values = {
            6: (4_132, 6_000_000),
            7: (3_987, 5_900_000),
            8: (4_048, 6_100_000),
        }
        return [
            {
                "year": year, "month": month,
                "month_name": self.MONTH_NAMES[month], "total_site": 1,
                "total_kwh": values.get(month, (None, None))[0],
                "total_value": values.get(month, (None, None))[1],
            }
            for year, month in periods
        ]


class FakeRegistry:
    def get(self, name):
        assert name == "pln"
        return SimpleNamespace(repository=FakeRepository())


def router():
    instance = AIRouter()
    instance.registry = FakeRegistry()
    return instance


def test_specific_month_and_both_metrics_are_deterministic():
    answer = router()._handle_pln_monthly_query(
        "KWH dan RPTAG site SBY001 bulan Juli 2026",
        "siteid", "SBY001",
    )
    assert "Juli 2026" in answer
    assert "KWH: 3.987 kWh" in answer
    assert "RPTAG: Rp 5.900.000" in answer
    assert "Agustus" not in answer
    assert "Total" not in answer


def test_router_does_not_call_gemini_for_specific_month_query():
    instance = router()
    instance._current_user_id = "test"
    instance._present = lambda *_: (_ for _ in ()).throw(AssertionError("Gemini called"))
    entity = SimpleNamespace(scope_type="siteid", scope_value="SBY001", period_months=1)
    answer = instance._handle_pln("KWH site SBY001 bulan Juli 2026", entity)
    assert "Juli 2026" in answer


def test_site_billing_without_month_uses_deterministic_rptag_without_gemini():
    instance = router()
    instance._current_user_id = "billing-test"
    instance._present = lambda *_: (_ for _ in ()).throw(AssertionError("Gemini called"))
    latest = {"month_name": "Agustus", "year": 2026, "total_value": 6_442_961}
    instance.registry = SimpleNamespace(get=lambda _: SimpleNamespace(
        analyze_site=lambda *_: SimpleNamespace(latest_month=latest),
        repository=FakeRepository(),
    ))
    entity = SimpleNamespace(scope_type="siteid", scope_value="SBY356", period_months=1)
    answer = instance._handle_pln("berapa tagihan sby356", entity)
    assert answer == "PLN siteid SBY356\n\nAgustus 2026: Rp 6.442.961"


def test_relative_billing_period_reads_each_prior_calendar_month_without_fallback():
    instance = router()
    instance._current_user_id = "relative-billing-test"
    instance._present = lambda *_: (_ for _ in ()).throw(AssertionError("Gemini called"))
    entity = SimpleNamespace(scope_type="siteid", scope_value="SBY064", period_months=3)
    three_months = instance._handle_pln("berapa tagihan sby064 3 bulan kebelakang", entity)
    assert "Juni 2026: Rp 6.000.000" in three_months
    assert "Juli 2026: Rp 5.900.000" in three_months
    assert "Agustus 2026: Rp 6.100.000" in three_months

    entity.period_months = 4
    four_months = instance._handle_pln("berapa tagihan sby064 4 bulan kebelakang", entity)
    assert "Mei 2026: data RPTAG tidak tersedia" in four_months
    assert "Juni 2026: Rp 6.000.000" in four_months
    assert "Juli 2026: Rp 5.900.000" in four_months
    assert "Agustus 2026: Rp 6.100.000" in four_months


def test_nop_scope_is_normalized_and_explicit_month_is_used():
    august_question = "bagaimana kondisi pln di NOP MALANG pada bulan Agustus"
    entity = router_module.EntityExtractor.extract(august_question)
    assert (entity.scope_type, entity.scope_value) == ("nop", "Malang")

    instance = router()
    instance._current_user_id = "nop-test"
    instance._present = lambda _, native: native
    august = instance._handle_pln(august_question, entity)
    assert august == "PLN nop Malang\n\nAgustus 2026: Rp 6.100.000"

    plain_entity = router_module.EntityExtractor.extract("bagaimana kondisi pln di NOP Malang")
    plain = instance._handle_pln("bagaimana kondisi pln di NOP Malang", plain_entity)
    assert "PLN nop Malang" in plain
    assert "Agustus 2026: Rp 6.100.000" in plain


def test_specific_month_rptag_does_not_call_gemini():
    instance = router()
    instance._current_user_id = "rptag-month-test"
    instance._present = lambda *_: (_ for _ in ()).throw(AssertionError("Gemini called"))
    entity = SimpleNamespace(scope_type="siteid", scope_value="SBY356", period_months=1)
    answer = instance._handle_pln("Berapa RPTAG site SBY356 bulan Agustus?", entity)
    assert "Agustus 2026: Rp 6.100.000" in answer


def test_pln_insight_uses_native_data_before_gemini():
    instance = router()
    instance._current_user_id = "insight-test"
    prompts = []
    instance.ai = SimpleNamespace(generate=lambda prompt: prompts.append(prompt) or "Pemakaian stabil.")
    entity = SimpleNamespace(scope_type="siteid", scope_value="SBY356", period_months=1)
    answer = instance._handle_pln(
        "bagaimana pemakaian listrik site SBY356 bulan Agustus?", entity,
    )
    assert "Agustus 2026: 4.048 kWh" in answer
    assert answer.endswith("Insight:\nPemakaian stabil.")
    assert "Data native:" in prompts[0]
    assert "4.048 kWh" in prompts[0]


def test_pln_insight_gemini_failure_returns_native_response():
    instance = router()
    instance._current_user_id = "insight-fallback-test"
    instance.ai = SimpleNamespace(generate=lambda _: (_ for _ in ()).throw(RuntimeError("unavailable")))
    entity = SimpleNamespace(scope_type="siteid", scope_value="SBY356", period_months=1)
    answer = instance._handle_pln(
        "bagaimana pemakaian listrik site SBY356 bulan Agustus?", entity,
    )
    assert answer == "PLN siteid SBY356\n\nAgustus 2026: 4.048 kWh"


def test_range_total_comparison_and_extremes():
    instance = router()
    range_answer = instance._handle_pln_monthly_query(
        "KWH site SBY001 bulan Juli sampai Agustus 2026",
        "siteid", "SBY001",
    )
    assert "Juli 2026" in range_answer and "Agustus 2026" in range_answer
    assert "Total" not in range_answer

    total_answer = instance._handle_pln_monthly_query(
        "total KWH dan RPTAG site SBY001 bulan Juli sampai Agustus 2026",
        "siteid", "SBY001",
    )
    assert "Total KWH: 8.035 kWh" in total_answer
    assert "Total RPTAG: Rp 12.000.000" in total_answer

    comparison = instance._handle_pln_monthly_query(
        "bandingkan KWH site SBY001 bulan Juli dan Agustus 2026",
        "siteid", "SBY001",
    )
    assert "Perubahan KWH: 61 kWh" in comparison

    highest = instance._handle_pln_monthly_query(
        "KWH tertinggi site SBY001 tahun 2026",
        "siteid", "SBY001",
    )
    assert "KWH tertinggi: 4.132 kWh (Juni 2026)" in highest


def test_june_to_august_range_is_inclusive_for_kwh_and_rptag_totals():
    instance = router()
    kwh = instance._handle_pln_monthly_query(
        "Total KWH site SBY356 Juni sampai Agustus 2026", "siteid", "SBY356",
    )
    assert "Juni 2026: 4.132 kWh" in kwh
    assert "Juli 2026: 3.987 kWh" in kwh
    assert "Agustus 2026: 4.048 kWh" in kwh
    assert "Total: 12.167 kWh" in kwh

    rptag = instance._handle_pln_monthly_query(
        "Total RPTAG site SBY356 Juni sampai Agustus 2026", "siteid", "SBY356",
    )
    assert "Juli 2026: Rp 5.900.000" in rptag
    assert "Total: Rp 18.000.000" in rptag


def test_pln_amr_is_not_routed_to_generic_amr_handler():
    assert IntentDetector.detect("status AMR PLN site SBY001") == "pln"


def test_capacity_formatter_uses_kva():
    assert AIRouter._format_pln_capacity(13200) == "13,2 kVA"


def test_threshold_respects_month_and_full_list_follow_up(monkeypatch):
    calls = []

    class FakeQueryService:
        def query_above(self, *args, **kwargs):
            calls.append(kwargs)
            return {
                "month": kwargs["month"], "month_name": "Juli",
                "rows": [
                    {"siteid": f"SBY{i}", "site_name": "Site", "kwh_pakai": 6000, "rptag": 1}
                    for i in range(kwargs.get("limit", 100))
                ],
            }

    monkeypatch.setattr(router_module, "PLNQueryService", FakeQueryService)
    instance = router()
    instance._current_user_id = "threshold-test"
    entity = SimpleNamespace(scope_type=None, scope_value=None)
    first = instance._handle_pln_variable_query("site mana KWH di atas 5000 bulan Juli 2026", entity)
    assert calls[-1]["month"] == 7
    assert "Sampling : 20 site" in first
    full = instance._handle_pln_variable_query("tampilkan semua", entity)
    assert calls[-1]["limit"] == 500
    assert "Jumlah site ditampilkan : 500" in full
    assert "\\n" not in first
    assert "PLN Variable Query\n\nMetric" in first


def test_gemini_retries_transient_error_then_returns_success(monkeypatch):
    attempts = []

    class Models:
        def generate_content(self, **kwargs):
            attempts.append(kwargs)
            if len(attempts) < 3:
                raise TimeoutError("temporary timeout")
            return SimpleNamespace(text="Gemini response")

    service = object.__new__(GeminiService)
    service.client = SimpleNamespace(models=Models())
    service.model = "test"
    monkeypatch.setattr(gemini_module.time, "sleep", lambda _: None)
    assert service.generate("question") == "Gemini response"
    assert len(attempts) == 3


def test_gemini_three_failures_use_native_fallback(monkeypatch):
    attempts = []

    class Models:
        def generate_content(self, **kwargs):
            attempts.append(kwargs)
            raise ConnectionError("offline")

    service = object.__new__(GeminiService)
    service.client = SimpleNamespace(models=Models())
    service.model = "test"
    monkeypatch.setattr(gemini_module.time, "sleep", lambda _: None)
    instance = object.__new__(AIRouter)
    instance.ai = service
    assert instance._present("requires Gemini", "Native System result") == "Native System result"
    assert len(attempts) == 3
