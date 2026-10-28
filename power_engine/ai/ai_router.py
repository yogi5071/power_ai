"""
AI Router
Power AI Copilot
"""

from power_engine.ai.gemini_service import GeminiService
from power_engine.ai.prompt_manager import PromptManager
from power_engine.ai.intent_detector import IntentDetector
from power_engine.ai.entity_extractor import EntityExtractor
from power_engine.ai.tool_registry import ToolRegistry
from power_engine.master_site_query_service import MasterSiteQueryService
from power_engine.pln_query_service import PLNQueryService
from power_engine.contract_service import ContractService
from telegram_bot.conversation import ConversationManager


class AIRouter:
    _PLN_MONTHS = {
        "januari": 1, "februari": 2, "maret": 3, "april": 4,
        "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
        "september": 9, "oktober": 10, "november": 11, "desember": 12,
    }



    def __init__(self):

        self.ai = GeminiService()

        self.registry = ToolRegistry()

        self.data_query = MasterSiteQueryService(
            self.registry.get("battery").repository
        )

        self.conversation = ConversationManager()
        self.contract_service = ContractService()

    def _present(
        self,
        prompt: str,
        fallback: str,
    ) -> str:

        try:

            return self.ai.generate(
                prompt
            )

        except RuntimeError:

            return fallback

        except Exception:

            return fallback

    @staticmethod
    def _format_pln_capacity(value):

        if value is None:

            return "-"

        value_kva = float(value) / 1000

        if value_kva.is_integer():

            return (
                f"{int(value_kva)} kVA"
            )

        return (
            f"{value_kva:.1f}"
            .replace(".", ",")
            + " kVA"
        )

    @staticmethod
    def _previous_complete_month_periods(count, today=None):
        """Return the prior `count` completed calendar months in order."""
        from datetime import date

        today = today or date.today()
        year, month = today.year, today.month
        periods = []
        for _ in range(count):
            month -= 1
            if month == 0:
                year, month = year - 1, 12
            periods.append((year, month))
        return list(reversed(periods))

    def _handle_pln_variable_query(self, question, entity):
        """Handle deterministic PLN threshold queries."""
        import re

        text = (question or "").lower().strip()

        # ------------------------------------------------------
        # FOLLOW-UP: FULL SITE LIST
        # ------------------------------------------------------
        asking_all_sites = any(
            phrase in text
            for phrase in (
                "site mana saja",
                "site apa saja",
                "daftar site",
                "list site",
                "semua site",
                "seluruh site",
                "tampilkan semua",
                "daftar lengkap",
                "tampilkan seluruh",
            )
        )

        context = self.conversation.get_context(
            self._current_user_id
        )
        variable_context = (
            context.get("pln_variable_query")
            if context
            else None
        )

        if asking_all_sites and variable_context:
            metric = variable_context.get("metric")
            operator = variable_context.get("operator")
            threshold = variable_context.get("threshold")
            year = variable_context.get("year")
            month = variable_context.get("month")
            scope_field = variable_context.get("scope_field")
            scope_value = variable_context.get("scope_value")

            service = PLNQueryService()

            if operator == "<":
                result = service.query_below(
                    metric,
                    threshold,
                    year,
                    month=month,
                    scope_field=scope_field,
                    scope_value=scope_value,
                    limit=500,
                )
            else:
                result = service.query_above(
                    metric,
                    threshold,
                    year,
                    month=month,
                    scope_field=scope_field,
                    scope_value=scope_value,
                    limit=500,
                )

            return self._format_pln_variable_result(
                result,
                metric,
                operator,
                threshold,
                scope_field,
                scope_value,
                year,
                full_list=True,
            )

        # ------------------------------------------------------
        # METRIC
        # ------------------------------------------------------
        rptag_keywords = (
            "rptag",
            "rp tag",
            "tagihan",
            "penagihan",
            "tagihan pln",
            "tagihan listrik",
            "biaya listrik",
            "biaya pln",
            "rekening listrik",
            "rekening pln",
        )

        kwh_keywords = (
            "kwh",
            "kwh pakai",
            "kwhpakai",
            "pemakaian kwh",
            "pemakaian listrik",
            "konsumsi listrik",
        )

        has_rptag = any(k in text for k in rptag_keywords)
        has_kwh = any(k in text for k in kwh_keywords)

        if not has_rptag and not has_kwh:
            return None

        # ------------------------------------------------------
        # OPERATOR
        # ------------------------------------------------------
        if any(
            k in text
            for k in (
                "di bawah",
                "dibawah",
                "kurang dari",
                "lebih kecil dari",
                "lebih kecil",
                "<",
            )
        ):
            operator = "<"
        elif any(
            k in text
            for k in (
                "di atas",
                "diatas",
                "lebih dari",
                "lebih besar dari",
                "lebih besar",
                ">",
            )
        ):
            operator = ">"
        else:
            return None

        # ------------------------------------------------------
        # THRESHOLD
        # ------------------------------------------------------
        threshold = None

        # Word form: satu juta / sejuta.
        if re.search(r"\bsejuta\b|\bsatu\s+juta\b", text):
            threshold = 1_000_000

        # Numeric million variants, including common typo "jutra".
        if threshold is None:
            juta_match = re.search(
                r"\b(\d+(?:[.,]\d+)?)\s*(?:juta|jutra|jta|jt)\b",
                text,
            )
            if juta_match:
                try:
                    threshold = (
                        float(
                            juta_match.group(1).replace(",", ".")
                        )
                        * 1_000_000
                    )
                except ValueError:
                    threshold = None

        # Explicit numeric/Rp values.
        if threshold is None:
            matches = re.findall(
                r"(?:rp\s*)?"
                r"(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)",
                text,
            )

            candidates = []
            for raw in matches:
                try:
                    normalized = raw
                    if "." in normalized and "," in normalized:
                        normalized = (
                            normalized.replace(".", "")
                            .replace(",", ".")
                        )
                    elif (
                        "." in normalized
                        and len(normalized.rsplit(".", 1)[-1]) == 3
                    ):
                        normalized = normalized.replace(".", "")
                    elif (
                        "," in normalized
                        and len(normalized.rsplit(",", 1)[-1]) == 3
                    ):
                        normalized = normalized.replace(",", "")
                    else:
                        normalized = normalized.replace(",", ".")

                    candidates.append(float(normalized))
                except ValueError:
                    pass

            if candidates:
                threshold = candidates[0]

        if threshold is None:
            return (
                "Saya menemukan pertanyaan PLN berdasarkan nilai, "
                "tetapi batas nilainya belum jelas.\n\n"
                "Contoh:\n"
                "â€¢ Site mana yang tagihannya di bawah 1 juta?\n"
                "â€¢ Site mana yang penagihan di bawah satu juta?\n"
                "â€¢ Site mana yang RPTAG di atas 5 juta?\n"
                "â€¢ Site mana yang KWH di atas 5000?"
            )

        # ------------------------------------------------------
        # METRIC RESOLUTION
        # ------------------------------------------------------
        if has_kwh and not has_rptag:
            metric = "kwh"
        else:
            metric = "rptag"

        if has_kwh and has_rptag:
            kwh_position = text.find("kwh")
            rptag_position = text.find("rptag")
            metric = (
                "kwh"
                if kwh_position > rptag_position
                else "rptag"
            )

        # ------------------------------------------------------
        # SCOPE
        # ------------------------------------------------------
        scope_field = getattr(entity, "scope_type", None)
        scope_value = getattr(entity, "scope_value", None)

        if scope_field == "nop" and scope_value:
            nop_alias = {
                "sby": "SURABAYA",
                "surabaya": "SURABAYA",
            }
            scope_value = nop_alias.get(
                str(scope_value).strip().lower(),
                str(scope_value).strip(),
            )

        # ------------------------------------------------------
        # YEAR / MONTH
        # ------------------------------------------------------
        year_match = re.search(r"\b(20\d{2})\b", text)
        year = int(year_match.group(1)) if year_match else 2026

        requested_months = self._pln_requested_months(text, year)
        month = (
            requested_months[0][1]
            if requested_months
            else None
        )
        requested_year = (
            requested_months[0][0]
            if requested_months
            else year
        )

        # ------------------------------------------------------
        # DATABASE QUERY
        # ------------------------------------------------------
        service = PLNQueryService()

        if operator == "<":
            result = service.query_below(
                metric,
                threshold,
                requested_year,
                month=month,
                scope_field=scope_field,
                scope_value=scope_value,
                limit=100,
            )
        else:
            result = service.query_above(
                metric,
                threshold,
                requested_year,
                month=month,
                scope_field=scope_field,
                scope_value=scope_value,
                limit=100,
            )

        if not result:
            return "Data PLN tidak ditemukan untuk query tersebut."

        result_month = (
            result.get("month")
            if isinstance(result, dict)
            else month
        )
        result_year = (
            result.get("year")
            if isinstance(result, dict)
            else requested_year
        )

        # ------------------------------------------------------
        # SAVE CONTEXT
        # ------------------------------------------------------
        self.conversation.set_context(
            self._current_user_id,
            intent="pln",
            scope_type=scope_field,
            scope_value=scope_value,
            pln_variable_query={
                "metric": metric,
                "operator": operator,
                "threshold": threshold,
                "year": result_year,
                "month": result_month,
                "scope_field": scope_field,
                "scope_value": scope_value,
            },
        )

        return self._format_pln_variable_result(
            result,
            metric,
            operator,
            threshold,
            scope_field,
            scope_value,
            result_year,
            full_list=False,
        )

    @staticmethod
    def _format_pln_variable_result(
        result,
        metric,
        operator,
        threshold,
        scope_field,
        scope_value,
        year,
        full_list=False,
    ):
        """Format hasil threshold PLN.

        Query pertama hanya menampilkan sampling maksimal 20 site.
        Follow-up daftar lengkap menampilkan seluruh row yang diberikan
        service (maksimal 500 sesuai batas service/repository saat ini).
        """

        if not result:
            return "Data PLN tidak ditemukan untuk query tersebut."

        rows = result.get("rows", []) if isinstance(result, dict) else result

        if not rows:
            metric_label = "RPTAG" if metric == "rptag" else "KWH"
            op_text = "di bawah" if operator == "<" else "di atas"
            value_text = f"{threshold:,.0f}".replace(",", ".")
            scope_text = (
                f" di {scope_field} {scope_value}"
                if scope_field and scope_value else ""
            )
            month_name = result.get("month_name") if isinstance(result, dict) else None
            return (
                f"Tidak ditemukan site dengan {metric_label} {op_text} "
                f"{value_text}{scope_text}"
                + (f" pada {month_name} {year}." if month_name else f" pada tahun {year}.")
            )

        lines = [
            "PLN Variable Query",
            "",
            f"Metric : {'RPTAG' if metric == 'rptag' else 'KWH'}",
            f"Kondisi : {'<' if operator == '<' else '>'} {threshold:,.0f}".replace(",", "."),
        ]

        if scope_field and scope_value:
            lines.append(f"Scope : {scope_field} {scope_value}")
        else:
            lines.append("Scope : Seluruh data PLN")

        if isinstance(result, dict):
            month_name = result.get("month_name")
            if month_name:
                lines.append(f"Bulan : {month_name} {year}")

        total_count = (
            result.get("total_count", result.get("count"))
            if isinstance(result, dict)
            else None
        )

        if total_count is not None:
            lines.append(
                f"Total : {total_count} site"
            )
        if full_list:
            lines.extend([
                "",
                f"Jumlah site ditampilkan : {len(rows)}",
                "",
                "Daftar site lengkap:",
            ])
        else:
            lines.extend([
                "",
                f"Sampling : {min(len(rows), 20)} site",
                "",
                "20 site pertama:",
            ])

        display_rows = rows if full_list else rows[:20]

        for i, row in enumerate(display_rows, 1):
            siteid = row.get("siteid", "-")
            site_name = row.get("site_name", "-")
            kwh = row.get("kwh_pakai")
            rptag = row.get("rptag")

            kwh_text = "-" if kwh is None else f"{float(kwh):,.0f}".replace(",", ".")
            rptag_text = "-" if rptag is None else f"Rp {int(rptag):,}".replace(",", ".")

            lines.append(
                f"{i}. {siteid} - {site_name} | KWH: {kwh_text} | RPTAG: {rptag_text}"
            )

        if not full_list and len(rows) >= 20:
            lines.extend([
                "",
                "Ketik 'site mana saja?' atau 'tampilkan semua' untuk melihat daftar lengkap hasil query ini.",
            ])

        return "\n".join(lines)

    def _handle_pln_sarpen_query(
        self,
        question,
        entity,
    ):

        pln_service = PLNQueryService()

        scope_type = entity.scope_type
        scope_value = entity.scope_value

        # ------------------------------------------------------
        # YEAR
        # ------------------------------------------------------

        import re

        text = (
            question
            or ""
        ).lower().strip()

        year_match = re.search(
            r"\b(20\d{2})\b",
            text,
        )

        year = (
            int(year_match.group(1))
            if year_match
            else 2026
        )

        # ------------------------------------------------------
        # QUERY SARPEN
        # ------------------------------------------------------

        result = (
            pln_service.query_schema_bayar(
                value="SARPEN",
                year=year,
                scope_field=scope_type,
                scope_value=scope_value,
                limit=20,
            )
        )

        total_count = int(
            result.get(
                "total_count",
                result.get("count", 0),
            )
            or 0
        )

        rows = (
            result.get("rows")
            or []
        )

        sampling_count = int(
            result.get(
                "sampling_count",
                len(rows),
            )
            or 0
        )

        # ------------------------------------------------------
        # NO DATA
        # ------------------------------------------------------

        if total_count == 0:

            if scope_type and scope_value:

                return (
                    "PLN SARPEN Query\n"
                    "\n"
                    "Schema Bayar : SARPEN\n"
                    f"Scope        : {scope_type} {scope_value}\n"
                    "Total        : 0 site\n"
                    "Sampling     : 0 site"
                )

            return (
                "PLN SARPEN Query\n"
                "\n"
                "Schema Bayar : SARPEN\n"
                "Scope        : Seluruh data PLN\n"
                "Total        : 0 site\n"
                "Sampling     : 0 site"
            )

        # ------------------------------------------------------
        # HEADER
        # ------------------------------------------------------

        lines = [
            "PLN SARPEN Query",
            "",
            "Schema Bayar : SARPEN",
        ]

        if scope_type and scope_value:

            lines.append(
                f"Scope        : {scope_type} {scope_value}"
            )

        else:

            lines.append(
                "Scope        : Seluruh data PLN"
            )

        lines.extend([
            f"Total        : {total_count} site",
            f"Sampling     : {sampling_count} site",
            "",
            f"{min(sampling_count, 20)} site pertama:",
        ])

        # ------------------------------------------------------
        # SITE LIST
        # ------------------------------------------------------

        for i, row in enumerate(
            rows[:20],
            1,
        ):

            siteid = row.get(
                "siteid",
                "-",
            )

            site_name = row.get(
                "site_name",
                "-",
            )

            lines.append(
                f"{i}. {siteid} - {site_name}"
            )

        # ------------------------------------------------------
        # FULL LIST FOLLOW-UP
        # ------------------------------------------------------

        if total_count > sampling_count:

            lines.extend([
                "",
                "Ketik 'site mana saja?' atau "
                "'tampilkan semua' untuk melihat daftar lengkap hasil query ini.",
            ])

        return "\n".join(lines)

    def _handle_contract(self, question, entity):
        """Handle deterministic contract queries and site lookups."""

        if not entity:
            return "Parameter kontrak tidak dapat ditemukan dari pertanyaan."

        field = entity.contract_subject
        scope_type = entity.scope_type
        scope_value = entity.scope_value

        import re

        explicit_site_id = None
        if scope_type == "siteid" and scope_value:
            site_pattern = (
                rf"\bSITE(?:\s+ID)?\s+{re.escape(str(scope_value))}\b"
            )
            if re.search(site_pattern, question or '', re.IGNORECASE):
                explicit_site_id = str(scope_value).strip()

        # None means this question should continue through normal routing.
        profile_fields = None
        if explicit_site_id and field is None:
            profile_fields = [
                ("Nama Site", "site_name"),
                ("Kategori", "kategori"),
                ("Nomor Kontrak", "no_contract"),
                ("Tanggal Akhir Kontrak (EOC)", "end_of_contract"),
                ("Last Recurring", "last_recurring"),
                ("Preventif Vandalisme", "preventif_vandalisme"),
                ("Kecamatan", "kecamatan"),
                ("Kabupaten/Kota", "kabupaten"),
                ("NOP", "nop_name"),
                ("Cluster", "cluster"),
            ]
        elif explicit_site_id and field == "no_contract" and not entity.contract_value:
            profile_fields = [("Nomor Kontrak", "no_contract")]
        elif explicit_site_id and field == "eoc" and not entity.eoc_operator:
            profile_fields = [("Tanggal Akhir Kontrak (EOC)", "end_of_contract")]

        if profile_fields is not None:
            try:
                profile = self.contract_service.get_site_profile(
                    explicit_site_id
                )
            except Exception as exc:
                return f"Query kontrak site gagal: {exc}"

            if not profile:
                return f"Data kontrak PLN tidak ditemukan untuk site {explicit_site_id}."

            lines = ["Data Kontrak PLN", ""]
            lines.append(f"Site ID : {profile.get('siteid') or explicit_site_id}")
            for label, key in profile_fields:
                value = profile.get(key)
                if value is None or not str(value).strip() or str(value).strip() == "0000-00-00":
                    value = "Tidak tersedia"
                lines.append(f"{label} : {value}")

            return "\n".join(lines)

        # CONTRACT URGENT ACTION LIST
        # List contracts reaching EOC within 90 days, ordered by nearest EOC.
        question_lower = str(question or "").lower()

        list_intent = any(
            term in question_lower
            for term in (
                "daftar",
                "list",
                "tampilkan",
                "sebutkan",
                "mana saja",
            )
        )

        urgent_intent = any(
            term in question_lower
            for term in (
                "urgent",
                "mendesak",
                "segera berakhir",
                "jatuh tempo",
                "perlu diperpanjang",
                "90 hari",
            )
        )

        if list_intent and urgent_intent:
            from datetime import date, timedelta

            today = date.today()
            deadline = today + timedelta(days=90)

            try:
                result = self.contract_service.query_eoc(
                    operator="between",
                    date_value=today.isoformat(),
                    date_value_to=deadline.isoformat(),
                    scope_field=scope_type,
                    scope_value=scope_value,
                    limit=20,
                )
            except Exception as exc:
                return f"Query daftar kontrak URGENT gagal: {exc}"

            rows = result.get("rows") or []
            total_count = int(
                result.get("total_count", len(rows)) or 0
            )
            sampling_count = int(
                result.get("sampling_count", len(rows)) or 0
            )

            scope_label = (
                f"{scope_type}: {scope_value}"
                if scope_type and scope_value
                else "Seluruh data contract"
            )

            lines = [
                "Daftar Kontrak URGENT",
                "",
                f"Tanggal evaluasi : {today.isoformat()}",
                f"Rentang EOC : {today.isoformat()} s/d {deadline.isoformat()}",
                f"Scope : {scope_label}",
                f"Total : {total_count} site",
                f"Sampling : {sampling_count} site",
            ]

            if rows:
                lines.extend([
                    "",
                    "Daftar tindakan, diurutkan dari EOC terdekat:",
                ])

                for row in rows:
                    siteid = row.get("siteid") or "-"
                    site_name = row.get("site_name") or "-"
                    raw_eoc = row.get("end_of_contract")

                    try:
                        eoc_date = date.fromisoformat(str(raw_eoc)[:10])
                        days_left = (eoc_date - today).days
                        eoc_label = eoc_date.isoformat()

                        if days_left == 0:
                            remaining = "jatuh tempo hari ini"
                        else:
                            remaining = f"{days_left} hari lagi"
                    except (TypeError, ValueError):
                        eoc_label = str(raw_eoc or "-")
                        remaining = "sisa hari tidak dapat dihitung"

                    lines.append(
                        f"- {siteid} | {site_name} | "
                        f"EOC: {eoc_label} | {remaining}"
                    )
            else:
                lines.extend([
                    "",
                    "Tidak ada kontrak dengan EOC dalam 90 hari ke depan.",
                ])

            if total_count > sampling_count:
                lines.extend([
                    "",
                    f"Menampilkan {sampling_count} dari {total_count} site.",
                    "Daftar ini merupakan sampel; masih ada site lain yang cocok.",
                ])

            lines.extend([
                "",
                "Prioritas URGENT dihitung berdasarkan EOC hari ini "
                "sampai 90 hari ke depan.",
            ])

            return "\n".join(lines)

        # CONTRACT LIST BY AREA
        # List contracts for an explicitly identified district/sub-district.
        if (
            field is None
            and scope_type in {"kabupaten", "kecamatan"}
            and scope_value
            and not any(
                term in str(question or "").lower()
                for term in (
                    "prioritas eoc",
                    "prioritas kontrak",
                    "kontrak prioritas",
                    "ringkasan eoc",
                    "ringkasan kontrak",
                    "status kontrak",
                    "kontrak expired",
                    "kontrak kadaluarsa",
                    "kontrak kedaluwarsa",
                    "kontrak sudah berakhir",
                    "kontrak yang sudah berakhir",
                    "segera berakhir",
                    "akan segera berakhir",
                    "mendekati eoc",
                    "kontrak jatuh tempo",
                    "jatuh tempo kontrak",
                    "kontrak paling mendesak",
                    "kontrak mendesak",
                    "perlu diperpanjang",
                    "perpanjangan kontrak",
                )
            )
        ):
            try:
                result = self.contract_service.list_sites(
                    scope_field=scope_type,
                    scope_value=scope_value,
                    limit=20,
                )
            except Exception as exc:
                return f"Query daftar kontrak gagal: {exc}"

            rows = result.get("rows") or []
            total_count = int(
                result.get("total_count", result.get("count", len(rows))) or 0
            )
            sampling_count = int(
                result.get("sampling_count", len(rows)) or 0
            )

            scope_labels = {
                "kabupaten": "Kabupaten",
                "kecamatan": "Kecamatan",
            }
            scope_label = (
                f"{scope_labels.get(scope_type, scope_type.title())} "
                f"{scope_value}"
            )

            if not rows:
                return (
                    "Daftar Kontrak PLN\n\n"
                    f"Scope : {scope_label}\n"
                    f"Total : {total_count} site\n"
                    "Tidak ada data kontrak yang cocok."
                )

            lines = [
                "Daftar Kontrak PLN",
                "",
                f"Scope : {scope_label}",
                f"Total : {total_count} site",
                f"Sampling : {sampling_count} site",
                "",
            ]

            for index, row in enumerate(rows, start=1):
                siteid = row.get("siteid") or "-"
                site_name = row.get("site_name") or "-"
                kategori = row.get("kategori") or "Tidak tersedia"
                no_contract = row.get("no_contract") or "Tidak tersedia"
                eoc = row.get("end_of_contract") or "Tidak tersedia"

                lines.extend([
                    f"{index}. {siteid} | {site_name}",
                    f"   Kategori : {kategori}",
                    f"   Nomor Kontrak : {no_contract}",
                    f"   EOC : {eoc}",
                    "",
                ])

            if total_count > sampling_count:
                lines.append(
                    f"Menampilkan {sampling_count} dari {total_count} site."
                )

            return "\n".join(lines)

        # CONTRACT EOC PRIORITY SUMMARY
        # Calculate operational priority from the actual EOC date.
        question_lower = str(question or "").lower()
        priority_terms = (
            "prioritas eoc",
            "prioritas kontrak",
            "kontrak prioritas",
            "ringkasan eoc",
            "ringkasan kontrak",
            "status kontrak",
            "kontrak expired",
            "kontrak kadaluarsa",
            "kontrak kedaluwarsa",
            "kontrak sudah berakhir",
            "kontrak yang sudah berakhir",
            "segera berakhir",
            "akan segera berakhir",
            "mendekati eoc",
            "kontrak jatuh tempo",
            "jatuh tempo kontrak",
            "kontrak paling mendesak",
            "kontrak mendesak",
            "perlu diperpanjang",
            "perpanjangan kontrak",
        )

        if any(term in question_lower for term in priority_terms):
            from datetime import date, timedelta

            today = date.today()
            urgent_end = today + timedelta(days=90)
            upcoming_start = urgent_end + timedelta(days=1)
            upcoming_end = today + timedelta(days=365)

            bucket_specs = [
                ("EXPIRED", "<", today.isoformat(), None, 3),
                (
                    "URGENT",
                    "between",
                    today.isoformat(),
                    urgent_end.isoformat(),
                    5,
                ),
                (
                    "UPCOMING",
                    "between",
                    upcoming_start.isoformat(),
                    upcoming_end.isoformat(),
                    5,
                ),
                (
                    "ACTIVE",
                    ">",
                    upcoming_end.isoformat(),
                    None,
                    1,
                ),
            ]

            results = {}
            try:
                for name, operator, date_from, date_to, limit in bucket_specs:
                    results[name] = self.contract_service.query_eoc(
                        operator=operator,
                        date_value=date_from,
                        date_value_to=date_to,
                        scope_field=scope_type,
                        scope_value=scope_value,
                        limit=limit,
                    )
            except Exception as exc:
                return f"Query prioritas EOC gagal: {exc}"

            counts = {
                name: int(
                    result.get("total_count", 0) or 0
                )
                for name, result in results.items()
            }

            scope_label = (
                f"{scope_type}: {scope_value}"
                if scope_type and scope_value
                else "Seluruh data contract"
            )

            lines = [
                "Prioritas EOC Kontrak PLN",
                "",
                f"Tanggal evaluasi : {today.isoformat()}",
                f"Scope : {scope_label}",
                "",
                "Ringkasan status:",
                f"- EXPIRED (sebelum {today.isoformat()}): "
                f"{counts['EXPIRED']} site",
                f"- URGENT (0-90 hari, sampai {urgent_end.isoformat()}): "
                f"{counts['URGENT']} site",
                f"- UPCOMING (91-365 hari, "
                f"{upcoming_start.isoformat()} s/d {upcoming_end.isoformat()}): "
                f"{counts['UPCOMING']} site",
                f"- ACTIVE (setelah {upcoming_end.isoformat()}): "
                f"{counts['ACTIVE']} site",
            ]

            expired_rows = results["EXPIRED"].get("rows") or []
            if expired_rows:
                lines.extend([
                    "",
                    "Contoh kontrak EXPIRED (maks. 3, EOC terlama):",
                ])
                for row in expired_rows[:3]:
                    lines.append(
                        f"- {row.get('siteid') or '-'} | "
                        f"{row.get('site_name') or '-'} | "
                        f"EOC: {row.get('end_of_contract') or '-'}"
                    )

            upcoming_rows = []
            for name in ("URGENT", "UPCOMING"):
                for row in results[name].get("rows") or []:
                    eoc = str(row.get("end_of_contract") or "")
                    upcoming_rows.append((eoc, name, row))

            upcoming_rows.sort(key=lambda item: (item[0], item[2].get("siteid") or ""))

            lines.extend(["", "Kontrak terdekat jatuh tempo (maks. 5):"])
            if upcoming_rows:
                for eoc, name, row in upcoming_rows[:5]:
                    lines.append(
                        f"- [{name}] {row.get('siteid') or '-'} | "
                        f"{row.get('site_name') or '-'} | EOC: {eoc or '-'}"
                    )
            else:
                lines.append(
                    "Tidak ada kontrak dengan EOC dalam 365 hari ke depan."
                )

            lines.extend([
                "",
                "Catatan: kategori dihitung dari EOC valid; "
                "tanggal kosong/tidak valid tidak masuk kategori.",
            ])
            return "\n".join(lines)

        if not field:
            return "Parameter kontrak tidak dapat ditentukan dari pertanyaan."

        # CONTRACT FIELD QUERY
        if field != "eoc":
            allowed_fields = {
                "kategori": "Kategori",
                "no_contract": "No Contract",
                "last_recurring": "Last Recurring",
                "preventif_vandalisme": "Preventif Vandalisme",
            }

            if field not in allowed_fields:
                return "Parameter kontrak tidak dapat ditemukan dari pertanyaan."

            value = entity.contract_value
            if not value:
                return f"Nilai {allowed_fields[field]} tidak dapat ditentukan dari pertanyaan."

            try:
                result = self.contract_service.query_field(
                    field=field,
                    value=value,
                    scope_field=scope_type,
                    scope_value=scope_value,
                    limit=20,
                )
            except Exception as exc:
                return f"Query kontrak gagal: {exc}"

            rows = result.get("rows", [])
            total_count = result.get("total_count", 0)
            sampling_count = result.get("sampling_count", len(rows))

            scope_label = (
                f"{scope_type}: {scope_value}"
                if scope_type and scope_value
                else "Seluruh data contract"
            )

            lines = [
                "Contract Query",
                "",
                f"Subject      : {allowed_fields[field]}",
                f"Value        : {value}",
                f"Scope        : {scope_label}",
                f"Total        : {total_count} site",
                f"Sampling     : {sampling_count} site",
            ]

            if rows:
                lines.extend(["", "Sampling site:"])
                for row in rows:
                    lines.append(
                        f"- {row.get('siteid') or '-'} | "
                        f"{row.get('site_name') or '-'}"
                    )
            else:
                lines.extend(["", "Tidak ada site yang cocok."])

            return "\n".join(lines)

        # EOC QUERY — retain the existing date-filter behavior.
        operator = entity.eoc_operator
        date_from = entity.eoc_date_from
        date_to = entity.eoc_date_to

        if not operator or not date_from:
            return "Operator atau tanggal EOC tidak dapat ditentukan."

        try:
            result = self.contract_service.query_eoc(
                operator=operator,
                date_value=date_from,
                date_value_to=date_to,
                scope_field=scope_type,
                scope_value=scope_value,
                limit=20,
            )
        except Exception as exc:
            return f"Query kontrak gagal: {exc}"

        total_count = result.get("total_count", 0)
        sampling_count = result.get("sampling_count", 0)
        rows = result.get("rows", [])

        scope_label = (
            f"{scope_type}: {scope_value}"
            if scope_type and scope_value
            else "Seluruh data contract"
        )

        if operator == "between":
            date_label = f"{date_from} s/d {date_to}"
        elif operator == "<":
            date_label = f"sebelum {date_from}"
        elif operator == "<=":
            date_label = f"sampai {date_to}"
        elif operator == ">":
            date_label = f"setelah {date_from}"
        elif operator == ">=":
            date_label = f"mulai {date_from}"
        else:
            date_label = str(date_from)

        lines = [
            "Contract / EOC Query",
            "",
            f"Scope        : {scope_label}",
            f"EOC          : {date_label}",
            f"Total        : {total_count} site",
            f"Sampling     : {sampling_count} site",
        ]

        if rows:
            lines.extend(["", "Sampling site:"])
            for row in rows:
                lines.append(
                    f"- {row.get('siteid') or '-'} | "
                    f"{row.get('site_name') or '-'} | "
                    f"EOC: {row.get('end_of_contract') or '-'}"
                )

        return "\n".join(lines)

    def _handle_pln_capacity(self, question, scope_type, scope_value, period_months):
        pln_service = self.registry.get('pln')
        if not scope_type or not scope_value:
            return 'Untuk mencari kapasitas PLN, sebutkan site yang dimaksud.\n\nContoh:\n• Berapa kapasitas PLN site SBY536?\n• Kapasitas PLN site BDO003 berapa?'
        result = pln_service.analyze(scope_type, scope_value, period_months)
        if result is None:
            return f'Data kapasitas PLN tidak ditemukan untuk {scope_type} {scope_value}.'
        if not result.has_capacity:
            return f'Data kapasitas PLN untuk {scope_type} {scope_value} belum tersedia.'
        kapasitas_text = self._format_pln_capacity(result.kapasitas_pln)
        return f'Informasi Kapasitas PLN\n\nScope : {scope_type} {scope_value}\nKapasitas PLN : {kapasitas_text}'

    def _handle_pln(
        self,
        question,
        entity,
    ):

        pln_service = self.registry.get(
            "pln"
        )

        # ------------------------------------------------------
        # SCOPE
        # ------------------------------------------------------

        scope_type = entity.scope_type
        scope_value = entity.scope_value

        # ------------------------------------------------------
        # PERIOD
        # ------------------------------------------------------

        period_months = (
            entity.period_months
            or 1
        )

        # ------------------------------------------------------
        # QUESTION TEXT
        # ------------------------------------------------------

        text = (
            question
            or ""
        ).lower().strip()

        # ======================================================
        # SARPEN
        #
        # SARPEN bukan PLN billing bulanan.
        # Tangani lebih dahulu agar tidak masuk ke generic
        # monthly / billing logic.
        # ======================================================

        if "sarpen" in text:

            return self._handle_pln_sarpen_query(
                question,
                entity,
            )

        # ======================================================
        # VARIABLE PLN QUERY
        # ======================================================

        variable_answer = self._handle_pln_variable_query(
            question,
            entity,
        )

        if variable_answer is not None:
            return variable_answer

        # ======================================================
        # CAPACITY FOLLOW-UP / DIRECT CAPACITY
        # ======================================================

        capacity_keywords = (
            "kapasitas pln",
            "kapasitas listrik",
            "daya pln",
            "daya listrik",
            "berapa kva",
            "berapa kva pln",
            "kva pln",
            "kapasitas daya",
            "kapasitasnya",
            "kapasitas nya",
            "dayanya",
            "daya nya",
            "kva nya",
            "kva-nya",
        )

        asking_capacity = any(
            keyword in text
            for keyword in capacity_keywords
        )

        if asking_capacity:
            return self._handle_pln_capacity(
                question,
                scope_type,
                scope_value,
                period_months,
            )
        # ======================================================
        # CAPACITY FOLLOW-UP / DIRECT CAPACITY
        # ======================================================

        capacity_keywords = (
            "kapasitas pln",
            "kapasitas listrik",
            "daya pln",
            "daya listrik",
            "berapa kva",
            "berapa kva pln",
            "kva pln",
            "kapasitas daya",
            "kapasitasnya",
            "kapasitas nya",
            "dayanya",
            "daya nya",
            "kva nya",
            "kva-nya",
        )

        asking_capacity = any(
            keyword in text
            for keyword in capacity_keywords
        )

        if asking_capacity:
            return self._handle_pln_capacity(
                question,
                scope_type,
                scope_value,
                period_months,
            )

        asking_site_billing = (
            scope_type == "siteid"
            and scope_value
            and any(keyword in text for keyword in (
                "tagihan", "biaya listrik", "rekening listrik", "rekening pln",
            ))
            and not any(keyword in text for keyword in (
                "total", "akumulasi", "bandingkan", "tertinggi", "terendah",
            ))
        )

        # Route a relative site-billing period to exact monthly records before
        # the generic PLN analysis path can turn it into a rolling summary.
        if asking_site_billing and period_months > 1:
            periods = self._previous_complete_month_periods(period_months)
            rows = pln_service.repository.get_months(
                "siteid", scope_value, periods,
            )
            lines = [f"PLN siteid {scope_value}", ""]
            for row in rows:
                rptag = row.get("total_value")
                value = (
                    self._pln_number(rptag, currency=True)
                    if rptag is not None
                    else "data RPTAG tidak tersedia"
                )
                lines.append(f"{row['month_name']} {row['year']}: {value}")
            return "\n".join(lines)

        monthly_answer = self._handle_pln_monthly_query(
            question,
            scope_type,
            scope_value,
            period_months,
        )

        if monthly_answer is not None:
            return monthly_answer

        # A direct site billing question without a named month is still a
        # factual RPTAG lookup. Use the latest month provided by PLNService.
        if asking_site_billing:
            result = pln_service.analyze_site(scope_value, period_months)
            latest = getattr(result, "latest_month", None) if result else None
            rptag = latest.get("total_value") if latest else None
            if latest and rptag is not None:
                return f"PLN siteid {scope_value}\n\n{latest.get('month_name')} {latest.get('year')}: {self._pln_number(rptag, currency=True)}"

        if not scope_type or not scope_value:
            return 'Untuk mencari tagihan PLN, sebutkan site atau scope yang dimaksud.\n\nContoh:\nâ€¢ Berapa tagihan PLN site SBY536?\nâ€¢ Berapa PLN 3 bulan terakhir site SBY536?'
        result = pln_service.analyze(scope_type, scope_value, period_months)
        if result is None:
            return f'Data PLN tidak ditemukan untuk {scope_type} {scope_value} pada periode yang diminta.'
        self.conversation.set_context(self._current_user_id, intent='pln', scope_type=scope_type, scope_value=scope_value, period_months=period_months)
        fallback = PromptManager.pln_text(result)
        return fallback

    def _handle_rectifier(
        self,
        question,
        entity,
    ):
        """
        Handle Rectifier questions.

        Data source:
            MasterSiteQueryService

        Scope:
            - province
            - kabupaten
            - kecamatan
            - nop
            - cluster
            - siteid

        Important:
        The deterministic query service remains the source of
        factual Rectifier numbers.

        Gemini is only used for presentation/insight when the
        question is a condition/summary question.
        """

        # ------------------------------------------------------
        # FACTUAL RECTIFIER DATA
        # ------------------------------------------------------

        factual_answer = (
            self.data_query.execute(
                question
            )
        )

        if factual_answer is None:

            return (
                "Data Rectifier tidak dapat ditemukan "
                "untuk pertanyaan tersebut."
            )

        # ------------------------------------------------------
        # SAVE RECTIFIER CONTEXT
        # ------------------------------------------------------

        self.conversation.set_context(
            self._current_user_id,
            intent="rectifier",
            scope_type=(
                entity.scope_type
                if entity
                else None
            ),
            scope_value=(
                entity.scope_value
                if entity
                else None
            ),
            site_id=(
                entity.site_id
                if entity
                else None
            ),
        )

        # ------------------------------------------------------
        # DETERMINE WHETHER USER IS ASKING FOR INSIGHT
        #
        # "Bagaimana kondisi..."
        # "Kondisi..."
        # "Analisis..."
        #
        # should receive AI interpretation.
        #
        # Numeric questions remain deterministic.
        # ------------------------------------------------------

        text = (
            question
            or ""
        ).lower().strip()

        asking_condition = any(
            phrase in text
            for phrase in (
                "bagaimana kondisi",
                "kondisi",
                "analisis",
                "insight",
                "gambaran",
                "status rectifier",
            )
        )

        # ------------------------------------------------------
        # CONDITION / SUMMARY
        # ------------------------------------------------------

        if asking_condition:

            prompt = self._rectifier_prompt(
                question,
                factual_answer,
            )

            return self._present(
                prompt,
                factual_answer,
            )

        # ------------------------------------------------------
        # NUMERIC / FACTUAL QUESTION
        #
        # Jangan biarkan Gemini mengubah angka.
        # ------------------------------------------------------

        return factual_answer

    @staticmethod
    def _rectifier_prompt(
        question,
        factual_answer,
    ):
        """
        Build a strict presentation prompt for Rectifier.

        Gemini receives already calculated factual data.

        Gemini MUST NOT:
        - recalculate numbers
        - invent numbers
        - change numbers
        - confuse site count with unit count
        - call obsolete site count the same as obsolete unit count
        """

        return f"""
Anda adalah AI Power Operation Copilot.

Jawab pertanyaan user berdasarkan DATA FAKTUAL yang diberikan.

PERTANYAAN USER:
{question}

DATA FAKTUAL:
{factual_answer}

ATURAN WAJIB:

1. Jangan mengubah angka apa pun dari DATA FAKTUAL.

2. Jangan menghitung ulang angka dari data mentah.

3. Jangan membuat angka baru.

4. Bedakan dengan jelas:
   - SITE LEVEL
   - UNIT RECTIFIER LEVEL

5. Jika DATA FAKTUAL menyebut:
   - obsolete site
   - non-obsolete site
   maka itu adalah jumlah SITE.

6. Jika DATA FAKTUAL menyebut:
   - total rectifier
   - obsolete rectifier
   - non-obsolete rectifier
   maka itu adalah jumlah UNIT.

7. Jangan menyamakan:
   "641 site obsolete"
   dengan
   "641 unit obsolete".

8. Jika user bertanya "bagaimana kondisi", berikan:
   - kondisi utama
   - interpretasi singkat
   - insight yang relevan terhadap scope yang ditanyakan.

9. Jangan menambahkan informasi yang tidak relevan dengan pertanyaan.

10. Jangan menampilkan total tambahan yang tidak diperlukan.

11. Jangan menggunakan istilah "provinsi" jika scope faktual bukan province.

12. Gunakan Bahasa Indonesia yang natural, ringkas, dan profesional.

13. Jika data menunjukkan obsolete relatif rendah, jangan menyebutnya
    "aman" secara mutlak. Gunakan bahasa seperti:
    "proporsinya relatif rendah" atau "sebagian kecil".

14. Jika terdapat perbedaan antara persentase obsolete site dan obsolete unit,
    jelaskan hanya jika relevan terhadap pertanyaan.

FORMAT JAWABAN:

Jika pertanyaan meminta kondisi:
[Kondisi utama]

Insight:
[interpretasi singkat berdasarkan DATA FAKTUAL]

Jika pertanyaan hanya meminta angka:
jawab angka yang diminta saja.

DATA FAKTUAL adalah sumber kebenaran utama.
"""

    def _handle_amr(
        self,
        question,
        entity,
    ):

        amr_service = self.registry.get(
            "amr"
        )

        # ------------------------------------------------------
        # CONTEXT
        # ------------------------------------------------------

        context = self.conversation.get_context(
            self._current_user_id
        )

        scope_type = (
            entity.scope_type
            or context.get("scope_type")
        )

        scope_value = (
            entity.scope_value
            or context.get("scope_value")
        )

        status = context.get(
            "status"
        )

        year = context.get(
            "year"
        )

        # ------------------------------------------------------
        # DETERMINE STATUS FROM QUESTION
        # ------------------------------------------------------

        text = (
            question
            or ""
        ).lower()

        if (
            "belum amr" in text
            or "belum ada amr" in text
            or "belum ada informasi amr" in text
        ):

            status = "Belum AMR"

        elif (
            "sudah amr" in text
            or "sudah terpasang amr" in text
        ):

            status = "AMR"

        elif (
            "tidak diketahui" in text
            or "belum ada informasi" in text
        ):

            status = "-"

        # ------------------------------------------------------
        # FOLLOW-UP:
        #
        # "Site mana saja?"
        # ------------------------------------------------------

        asking_sites = (
            "site mana saja" in text
            or "site apa saja" in text
            or "daftar site" in text
            or "list site" in text
        )

        if asking_sites:

            if (
                not scope_type
                or not scope_value
            ):

                return (
                    "Saya belum mengetahui "
                    "scope yang dimaksud.\n\n"
                    "Contoh:\n"
                    "Site mana saja yang belum AMR "
                    "di Kecamatan Waru?"
                )

            if not status:

                status = "Belum AMR"

            result = amr_service.analyze_sites(
                scope_type,
                scope_value,
                status,
                year,
            )

            if result is None:

                return (
                    f"Tidak ditemukan data site "
                    f"dengan status {status} "
                    f"untuk {scope_type} "
                    f"{scope_value}."
                )

            lines = [
                "ðŸ“¡ Daftar Site",
                "",
                f"Scope : "
                f"{scope_type} "
                f"{scope_value}",
                f"Status : {status}",
                f"Total : "
                f"{len(result.sites)} site",
                "",
            ]

            for index, site in enumerate(
                result.sites,
                start=1,
            ):

                if isinstance(
                    site,
                    dict
                ):

                    site_id = (
                        site.get("siteid")
                        or site.get("site_id")
                        or site.get("SITEID")
                    )

                else:

                    site_id = str(
                        site
                    )

                lines.append(
                    f"{index}. {site_id}"
                )

            # --------------------------------------------------
            # KEEP CONTEXT
            # --------------------------------------------------

            self.conversation.set_context(
                self._current_user_id,
                intent="amr",
                scope_type=scope_type,
                scope_value=scope_value,
                status=status,
                year=year,
            )

            return "\n".join(
                lines
            )

        # ======================================================
        # SUMMARY
        # ======================================================

        if (
            not scope_type
            or not scope_value
        ):

            return (
                "Untuk mencari status AMR, "
                "sebutkan scope yang dimaksud.\n\n"
                "Contoh:\n"
                "â€¢ Berapa site yang belum AMR "
                "di Kecamatan Waru?\n"
                "â€¢ Berapa site yang sudah AMR "
                "di Kabupaten Sidoarjo?"
            )

        result = amr_service.analyze(
            scope_type,
            scope_value,
            year,
        )

        if result is None:

            return (
                f"Data AMR tidak ditemukan untuk "
                f"{scope_type} {scope_value}."
            )

        # ------------------------------------------------------
        # SAVE CONTEXT
        # ------------------------------------------------------

        self.conversation.set_context(
            self._current_user_id,
            intent="amr",
            scope_type=scope_type,
            scope_value=scope_value,
            status=status,
            year=year,
        )

        # ------------------------------------------------------
        # DETERMINISTIC RESPONSE
        # ------------------------------------------------------

        fallback = (
            "AMR Summary\n\n"
            f"Scope : "
            f"{scope_type} "
            f"{scope_value}\n"
            f"Total Site : "
            f"{result.total_site}\n"
            f"AMR : "
            f"{result.total_amr} "
            f"({result.amr_percentage:.2f}%)\n"
            f"Belum AMR : "
            f"{result.total_belum_amr} "
            f"({result.belum_amr_percentage:.2f}%)\n"
            f"- (Belum ada informasi) : "
            f"{result.total_unknown} "
            f"({result.unknown_percentage:.2f}%)"
        )

        return fallback

    def ask(self, question: str, user_id=None) -> str:
        self._current_user_id = user_id if user_id is not None else 'default'
        intent = IntentDetector.detect(question)
        entity = EntityExtractor.extract(question)
        context = self.conversation.get_context(self._current_user_id)
        if context:
            question_text = (question or '').lower()
            is_new_global_pln_query = intent == 'pln' and any((phrase in question_text for phrase in ('site mana', 'site apa', 'semua site', 'seluruh site'))) and not any((phrase in question_text for phrase in ('site mana saja', 'site apa saja', 'tampilkan semua', 'daftar lengkap', 'seluruh hasil')))
            if intent == 'general':
                question_lower = (question or '').lower().strip()
                conversational_general = any((phrase in question_lower for phrase in ('makasih', 'terima kasih', 'terimakasih', 'thanks', 'thank you', 'sip', 'sipp', 'oke', 'ok', 'okay', 'siap', 'mantap', 'good', 'nice')))
                if conversational_general:
                    return self.ai.chat(question)
                previous_intent = context.get('intent')
                if previous_intent:
                    intent = previous_intent
            if not entity.scope_type and not is_new_global_pln_query:
                entity.scope_type = context.get('scope_type')
            if not entity.scope_value and not is_new_global_pln_query:
                entity.scope_value = context.get('scope_value')
            if not entity.site_id:
                entity.site_id = context.get('site_id')
            if not entity.period_months:
                entity.period_months = context.get('period_months')
        if intent == 'contract':
            return self._handle_contract(question, entity)
        if intent == 'pln':
            return self._handle_pln(question, entity)
        if intent == 'amr':
            return self._handle_amr(question, entity)
        if intent == 'rectifier':
            return self._handle_rectifier(question, entity)
        if intent == 'outage':
            if not entity.scope_type or not entity.scope_value:
                return 'Untuk mencari data pemadaman, sebutkan scope yang dimaksud: Site, Kecamatan, Kabupaten, NOP, atau Cluster.\n\nContoh:\nBerapa rata-rata pemadaman Kecamatan Taman?'
            result = self.registry.get('outage').analyze(entity.scope_type, entity.scope_value)
            if result is None:
                return f'Data pemadaman tidak ditemukan untuk {entity.scope_type} {entity.scope_value}.'
            fallback = PromptManager.outage_text(result)
            return self._present(PromptManager.outage_prompt(question, result), fallback)
        if intent == 'battery_outage':
            if not entity.site_id:
                return 'Untuk analisis battery dan pemadaman sekaligus, sebutkan Site ID.\n\nContoh:\nBagaimana kondisi battery ABC123 dan pemadamannya?'
            battery = self.registry.get('battery').analyze_site(entity.site_id)
            if battery is None:
                return f'Site {entity.site_id} tidak ditemukan.'
            outage = self.registry.get('outage').analyze('siteid', entity.site_id)
            if outage is None:
                return PromptManager.battery_text(battery) + '\n\nData outage site belum tersedia.'
            fallback = PromptManager.battery_text(battery) + '\n\n' + PromptManager.outage_text(outage)
            return self._present(PromptManager.battery_outage_prompt(question, battery, outage), fallback)
        if intent == 'battery':
            site_id = entity.site_id
            province = getattr(entity, 'province', None)
            text = (question or '').lower().strip()
            if not province and ('jawa timur' in text or 'jatim' in text):
                province = 'Jawa Timur'
            battery_service = self.registry.get('battery')
            nop = None
            if getattr(entity, 'scope_type', None) == 'nop':
                nop = getattr(entity, 'scope_value', None)
            if nop:
                summary = battery_service.analyze_nop(nop)
                if summary is None:
                    return f'Tidak ditemukan data site untuk NOP {nop}.'
                return self._present(PromptManager.battery_kabupaten_prompt(question, summary), PromptManager.battery_kabupaten_text(summary))
            if province:
                summary = battery_service.analyze_province(province)
                if summary is None:
                    return f'Tidak ditemukan data site untuk Provinsi {province}.'
                return self._present(PromptManager.battery_kabupaten_prompt(question, summary), PromptManager.battery_kabupaten_text(summary))
            kabupaten = entity.kabupaten or EntityExtractor.extract_kabupaten(question)
            kecamatan = entity.kecamatan or EntityExtractor.extract_kecamatan(question)
            if kabupaten:
                summary = battery_service.analyze_kabupaten(kabupaten)
                if summary is None:
                    return f'Tidak ditemukan data site untuk Kabupaten {kabupaten}.'
                return self._present(PromptManager.battery_kabupaten_prompt(question, summary), PromptManager.battery_kabupaten_text(summary))
            if kecamatan:
                summary = battery_service.analyze_kecamatan(kecamatan)
                if summary is None:
                    return f'Tidak ditemukan data site untuk Kecamatan {kecamatan}.'
                return self._present(PromptManager.battery_kabupaten_prompt(question, summary), PromptManager.battery_kabupaten_text(summary))
            if site_id is None:
                return 'Silakan sebutkan Site ID, Kecamatan, Kabupaten, atau Provinsi.\n\nContoh:\nâ€¢ Bagaimana kondisi battery ABC123?\nâ€¢ Bagaimana kondisi battery Kecamatan Waru?\nâ€¢ Bagaimana kondisi battery Kabupaten Sidoarjo?\nâ€¢ Bagaimana kondisi battery Jawa Timur?'
            result = battery_service.analyze_site(site_id)
            if result is None:
                return f'Site {site_id} tidak ditemukan.'
            return self._present(PromptManager.battery_prompt(question, result), PromptManager.battery_text(result))
        factual_answer = self.data_query.execute(question)
        if factual_answer is not None:
            return self._present(PromptManager.data_query_prompt(question, factual_answer), factual_answer)
        return self._present(PromptManager.general_prompt(question), 'Layanan AI tidak tersedia. Silakan periksa konfigurasi Gemini.')

    @classmethod
    def _pln_requested_months(cls, text, year):
        """Return explicitly requested (year, month) values, in user order."""
        import re

        month_pattern = "|".join(cls._PLN_MONTHS)
        range_match = re.search(
            rf"\b({month_pattern})\b(?:\s+(20\d{{2}}))?\s+"
            rf"sampai\s+\b({month_pattern})\b(?:\s+(20\d{{2}}))?",
            text.lower(),
        )

        if range_match:
            start_month = cls._PLN_MONTHS[range_match.group(1)]
            end_month = cls._PLN_MONTHS[range_match.group(3)]
            start_year = int(range_match.group(2) or range_match.group(4) or year)
            end_year = int(range_match.group(4) or range_match.group(2) or year)

            # "Desember 2025 sampai Februari 2026" is valid; when the
            # year is omitted on both sides, preserve the current-year range.
            if end_year < start_year:
                return []

            periods = []
            current_year, current_month = start_year, start_month
            while (current_year, current_month) <= (end_year, end_month):
                periods.append((current_year, current_month))
                current_month += 1
                if current_month == 13:
                    current_month = 1
                    current_year += 1
            return periods

        values = []
        for match in re.finditer(r"\b(" + month_pattern + r")\b(?:\s+(20\d{2}))?", text.lower()):
            values.append((int(match.group(2) or year), cls._PLN_MONTHS[match.group(1)]))
        return values

    @staticmethod
    def _pln_number(value, currency=False):
        if value is None:
            return "-"
        rendered = f"{float(value):,.0f}".replace(",", ".")
        return f"Rp {rendered}" if currency else f"{rendered} kWh"

    def _handle_pln_monthly_query(self, question, scope_type, scope_value, period_months=1):
        """Answer factual monthly PLN requests without Gemini.

        Explicit months are sent directly to the repository.  This is
        deliberately separate from PLNService.analyze(), whose rolling period
        semantics are appropriate only when the user did not name a month.
        """
        import re

        text = (question or "").lower()
        has_kwh = "kwh" in text or "pemakaian" in text or "konsumsi" in text
        has_rptag = any(word in text for word in ("rptag", "tagihan", "rekening", "biaya"))
        comparison = any(word in text for word in ("bandingkan", "perbandingan", "dibanding"))
        highest = any(word in text for word in ("tertinggi", "paling tinggi", "terbesar"))
        lowest = any(word in text for word in ("terendah", "paling rendah", "terkecil"))
        wants_total = any(phrase in text for phrase in (
            "total kwh", "total rptag", "jumlah keseluruhan", "akumulasi", "total",
        ))
        wants_insight = any(phrase in text for phrase in (
            "bagaimana", "tren", "analisis", "insight",
        ))
        is_nop_condition = scope_type == "nop" and "kondisi pln" in text
        year_match = re.search(r"\b(20\d{2})\b", text)
        year = int(year_match.group(1)) if year_match else 2026
        periods = self._pln_requested_months(text, year)

        # Only intercept factual monthly questions.  A profile question such
        # as "customer PLN site ..." remains on the profile path below.
        if not (has_kwh or has_rptag or comparison or highest or lowest or is_nop_condition):
            return None
        if not scope_type or not scope_value:
            return None

        # Highest/lowest is meaningful across all months in the selected year.
        if (highest or lowest) and not periods:
            periods = [(year, month) for month in range(1, 13)]
        if is_nop_condition and not periods:
            periods = self._previous_complete_month_periods(1)
        # A rolling request may use PLNService; an explicit calendar month may
        # never silently fall back to the latest available month.
        if not periods:
            if period_months > 1:
                native_result = self.registry.get('pln').analyze(scope_type, scope_value, period_months)
                if native_result is None:
                    return None
                self.conversation.set_context(self._current_user_id, intent='pln', scope_type=scope_type, scope_value=scope_value, period_months=period_months)
                return PromptManager.pln_text(native_result, include_total=wants_total)
        if not periods and not wants_insight:
            return None

        if periods:
            repository_scope = "union" if scope_type == "province" else scope_type
            rows = self.registry.get("pln").repository.get_months(repository_scope, scope_value, periods)
        else:
            native_result = self.registry.get("pln").analyze(
                scope_type, scope_value, period_months,
            )
            rows = getattr(native_result, "months", []) if native_result else []
        metrics = []
        if has_kwh:
            metrics.append(("KWH", "total_kwh", False))
        if has_rptag:
            metrics.append(("RPTAG", "total_value", True))
        if not metrics:
            metrics.append(("RPTAG", "total_value", True))

        available = [row for row in rows if any(row.get(key) is not None for _, key, _ in metrics)]
        if not available:
            requested = ", ".join(f"{row['month_name']} {row['year']}" for row in rows)
            return f"Data PLN tidak tersedia untuk {scope_type} {scope_value} pada {requested}."

        title = f"PLN {scope_type} {scope_value}"
        lines = [title, ""]
        if highest or lowest:
            direction = "tertinggi" if highest else "terendah"
            for label, key, currency in metrics:
                candidates = [row for row in rows if row.get(key) is not None]
                if not candidates:
                    lines.append(f"{label} {direction}: data tidak tersedia")
                    continue
                selected = (max if highest else min)(candidates, key=lambda row: row[key])
                lines.append(f"{label} {direction}: {self._pln_number(selected[key], currency)} ({selected['month_name']} {selected['year']})")
            return self._pln_insight_response(question, "\n".join(lines), wants_insight)

        for row in rows:
            if len(metrics) == 1:
                _, key, currency = metrics[0]
                values = self._pln_number(row.get(key), currency)
            else:
                values = " | ".join(
                    f"{label}: {self._pln_number(row.get(key), currency)}"
                    for label, key, currency in metrics
                )
            lines.append(f"{row['month_name']} {row['year']}: {values}")

        if wants_total:
            totals = []
            for label, key, currency in metrics:
                values = [row[key] for row in rows if row.get(key) is not None]
                total_label = "Total" if len(metrics) == 1 else f"Total {label}"
                totals.append(f"{total_label}: {self._pln_number(sum(values), currency)}" if values else f"{total_label}: -")
            lines.extend(["", *totals])
        elif comparison and len(rows) >= 2:
            lines.append("")
            for label, key, currency in metrics:
                first, last = rows[0].get(key), rows[-1].get(key)
                if first is not None and last is not None:
                    lines.append(f"Perubahan {label}: {self._pln_number(last - first, currency)}")
        return self._pln_insight_response(question, "\n".join(lines), wants_insight)

    def _pln_insight_response(self, question, native_response, wants_insight):
        """Append optional Gemini commentary without giving it control of facts."""
        if not wants_insight:
            return native_response

        prompt = (
            "Berikan insight PLN singkat berdasarkan data native berikut. "
            "Jangan membuat, mengubah, atau menyebut angka selain yang ada di data. "
            "Jika data tidak cukup, katakan demikian.\n\n"
            f"Pertanyaan pengguna: {question}\n\n"
            f"Data native:\n{native_response}"
        )
        insight = self._present(prompt, native_response)

        if insight == native_response:
            return native_response

        return f"{native_response}\n\nInsight:\n{insight}"

