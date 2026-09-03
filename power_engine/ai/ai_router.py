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
from telegram_bot.conversation import ConversationManager


class AIRouter:

    def __init__(self):

        self.ai = GeminiService()

        self.registry = ToolRegistry()

        self.data_query = MasterSiteQueryService(
            self.registry.get("battery").repository
        )

        self.conversation = ConversationManager()

    # ==========================================================
    # AI PRESENTATION
    # ==========================================================

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

    # ==========================================================
    # PLN CAPACITY FORMATTER
    #
    # Database:
    #
    #   10600 VA
    #
    # Presentation:
    #
    #   10,6 kVA
    #
    # Database value tidak diubah.
    # Hanya format tampilan yang dikonversi.
    # ==========================================================

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

    # ==========================================================
    # PLN VARIABLE QUERY
    # ==========================================================

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
                "• Site mana yang tagihannya di bawah 1 juta?\n"
                "• Site mana yang penagihan di bawah satu juta?\n"
                "• Site mana yang RPTAG di atas 5 juta?\n"
                "• Site mana yang KWH di atas 5000?"
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
            )
        else:
            result = service.query_above(
                metric,
                threshold,
                requested_year,
                month=month,
                scope_field=scope_field,
                scope_value=scope_value,
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

    # ==========================================================
    # PLN
    # ==========================================================

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
        # VARIABLE PLN QUERY
        # ======================================================

        variable_answer = self._handle_pln_variable_query(
            question,
            entity,
        )

        if variable_answer is not None:
            return variable_answer

        monthly_answer = self._handle_pln_monthly_query(
            question,
            scope_type,
            scope_value,
            period_months,
        )

        if monthly_answer is not None:
            return monthly_answer

        # A direct site billing question without a named month is still a
        # factual RPTAG lookup.  Use the latest month provided by PLNService,
        # rather than falling through to the generic monthly presentation.
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

        if asking_site_billing:
            # "N bulan kebelakang" is a closed historical range ending in
            # the prior calendar month, never a rolling/latest-month fallback.
            if period_months > 1:
                from datetime import date

                today = date.today()
                year, month = today.year, today.month - 1
                if month == 0:
                    year, month = year - 1, 12

                periods = []
                for _ in range(period_months):
                    periods.append((year, month))
                    month -= 1
                    if month == 0:
                        year, month = year - 1, 12
                periods.reverse()

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
                    lines.append(
                        f"{row['month_name']} {row['year']}: {value}"
                    )
                return "\n".join(lines)

            result = pln_service.analyze_site(scope_value, period_months)
            latest = getattr(result, "latest_month", None) if result else None
            rptag = latest.get("total_value") if latest else None

            if latest and rptag is not None:
                return "\n".join((
                    f"PLN siteid {scope_value}",
                    "",
                    f"{latest['month_name']} {latest['year']}: "
                    f"{self._pln_number(rptag, currency=True)}",
                ))

            return f"Data RPTAG tidak tersedia untuk siteid {scope_value}."

        # ======================================================
        # SITE PROFILE / CONDITION QUESTION
        #
        # Pertanyaan seperti:
        #   "Bagaimana kondisi PLN site SBY356?"
        #   "Siapa pelanggan PLN site SBY356?"
        #   "Berapa daya PLN site SBY356?"
        #
        # harus membaca PROFILE site secara langsung.
        # Jangan bergantung pada availability monthly bulan berjalan.
        # ======================================================

        profile_keywords = (
            "bagaimana kondisi",
            "kondisi pln",
            "kondisi listrik",
            "profil pln",
            "profile pln",
            "informasi pln",
            "siapa pelanggan",
            "customer",
            "nama pelanggan",
            "pelanggan id",
            "customer id",
            "tower owner",
            "source power",
            "sumber listrik",
            "status amr",
            "sudah amr",
            "belum amr",
            "jenis inquiry",
            "type tarif",
            "tipe tarif",
            "tarif",
            "schema bayar",
            "skema bayar",
            "schema pembayaran",
            "skema pembayaran",
            "tp nontp",
            "tp-nontp",
        )

        asking_profile = any(
            keyword in text
            for keyword in profile_keywords
        )

        # Hanya site-level profile yang ditangani di sini.
        # Query aggregate tetap memakai jalur monthly/aggregate.
        if asking_profile and scope_type == "siteid" and scope_value:

            result = pln_service.analyze_site(
                scope_value,
                period_months,
            )

            if result is None:
                return (
                    f"Data PLN tidak ditemukan untuk siteid "
                    f"{scope_value}."
                )

            profile = getattr(result, "profile", None) or {}

            if not profile:
                return (
                    f"Profile PLN tidak ditemukan untuk siteid "
                    f"{scope_value}."
                )

            # --------------------------------------------------
            # PROFILE FIELDS
            # --------------------------------------------------

            def profile_value(key):
                value = profile.get(key)
                if value is None or str(value).strip() == "":
                    return "-"
                return str(value)

            siteid = profile_value("siteid")
            site_name = profile_value("site_name")
            pelanggan_id = profile_value("pelanggan_id")
            nama_pelanggan = profile_value("nama_pelanggan")
            tower_owner = profile_value("tower_owner")
            source_power = profile_value("source_power")
            amr = profile_value("amr")
            daya = profile.get("daya")
            jenis_inquiry = profile_value("jenis_inquiry")
            type_tarif = profile_value("type_tarif")
            schema_bayar = profile_value("schema_bayar")
            tp_nontp = profile_value("tp_nontp")

            if daya is None:
                daya_text = "-"
            else:
                daya_text = self._format_pln_capacity(daya)

            # --------------------------------------------------
            # LATEST AVAILABLE MONTH
            #
            # September yang NULL tidak berarti site tidak punya
            # data. PLNService sudah melakukan fallback ke bulan
            # terakhir yang tersedia.
            # --------------------------------------------------

            latest = getattr(result, "latest_month", None) or {}

            lines = [
                "⚡ KONDISI PLN SITE",
                "",
                f"Site ID        : {siteid}",
                f"Site Name      : {site_name}",
                "",
                f"Pelanggan ID   : {pelanggan_id}",
                f"Nama Pelanggan : {nama_pelanggan}",
                "",
                f"Tower Owner    : {tower_owner}",
                f"Source Power   : {source_power}",
                f"AMR            : {amr}",
                f"Daya           : {daya_text}",
                f"Jenis Inquiry  : {jenis_inquiry}",
                f"Type Tarif     : {type_tarif}",
                f"Schema Bayar   : {schema_bayar}",
                f"TP/NONTP       : {tp_nontp}",
            ]

            if latest:
                month_name = latest.get("month_name", "-")
                latest_year = latest.get("year", profile.get("tahun", "-"))
                kwh = latest.get("total_kwh")
                rptag = latest.get("total_value")

                kwh_text = (
                    "-" if kwh is None
                    else f"{float(kwh):,.0f}".replace(",", ".") + " kWh"
                )
                rptag_text = (
                    "-" if rptag is None
                    else "Rp " + f"{int(rptag):,}".replace(",", ".")
                )

                lines.extend([
                    "",
                    "📊 PEMAKAIAN TERAKHIR",
                    f"Bulan          : {month_name} {latest_year}",
                    f"KWH Pakai      : {kwh_text}",
                    f"RPTAG          : {rptag_text}",
                ])

                requested_month = None
                if hasattr(result, "months") and result.months:
                    requested_month = result.months[-1]

                if requested_month:
                    requested_has_data = requested_month.get("total_site", 0) > 0
                    if not requested_has_data and requested_month.get("month_name") != month_name:
                        lines.extend([
                            "",
                            f"ℹ️ Data {requested_month.get('month_name')} {requested_month.get('year')} "
                            "belum tersedia.",
                            f"Data terakhir yang tersedia: {month_name} {latest_year}.",
                        ])

            return "\n".join(lines)

        # ======================================================
        # CAPACITY QUESTION
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
        )

        asking_capacity = any(
            keyword in text
            for keyword in capacity_keywords
        )

        # ======================================================
        # CAPACITY
        # ======================================================

        if asking_capacity:

            # --------------------------------------------------
            # CAPACITY REQUIRES SCOPE
            # --------------------------------------------------

            if (
                not scope_type
                or not scope_value
            ):

                return (
                    "Untuk mencari kapasitas PLN, "
                    "sebutkan site yang dimaksud.\n\n"
                    "Contoh:\n"
                    "• Berapa kapasitas PLN site SBY536?\n"
                    "• Kapasitas PLN site BDO003 berapa?"
                )

            # --------------------------------------------------
            # GET PLN DATA
            # --------------------------------------------------

            result = pln_service.analyze(
                scope_type,
                scope_value,
                period_months,
            )

            if result is None:

                return (
                    f"Data kapasitas PLN tidak ditemukan "
                    f"untuk {scope_type} "
                    f"{scope_value}."
                )

            # --------------------------------------------------
            # CHECK CAPACITY
            # --------------------------------------------------

            if not result.has_capacity:

                return (
                    f"Data kapasitas PLN untuk "
                    f"{scope_type} {scope_value} "
                    f"belum tersedia."
                )

            # --------------------------------------------------
            # DATABASE VALUE
            #
            # Database menyimpan satuan VA.
            # --------------------------------------------------

            kapasitas = result.kapasitas_pln

            # --------------------------------------------------
            # PRESENTATION VALUE
            #
            # 10600 VA -> 10,6 kVA
            # --------------------------------------------------

            kapasitas_text = (
                self._format_pln_capacity(
                    kapasitas
                )
            )

            # --------------------------------------------------
            # DETERMINISTIC RESPONSE
            #
            # Jangan kirim pertanyaan kapasitas ke Gemini.
            # Nilai harus berasal langsung dari database.
            # --------------------------------------------------

            return (
                "Informasi Kapasitas PLN\n\n"
                f"Scope : "
                f"{scope_type} "
                f"{scope_value}\n"
                f"Kapasitas PLN : "
                f"{kapasitas_text}"
            )

        # ======================================================
        # NORMAL PLN BILLING
        # ======================================================

        if (
            not scope_type
            or not scope_value
        ):

            return (
                "Untuk mencari tagihan PLN, "
                "sebutkan site atau scope yang dimaksud.\n\n"
                "Contoh:\n"
                "• Berapa tagihan PLN site SBY536?\n"
                "• Berapa PLN 3 bulan terakhir site SBY536?"
            )

        # ------------------------------------------------------
        # GET PLN DATA
        # ------------------------------------------------------

        result = pln_service.analyze(
            scope_type,
            scope_value,
            period_months,
        )

        if result is None:

            return (
                f"Data PLN tidak ditemukan untuk "
                f"{scope_type} {scope_value} "
                f"pada periode yang diminta."
            )

        # ------------------------------------------------------
        # SAVE PLN CONTEXT
        # ------------------------------------------------------

        self.conversation.set_context(
            self._current_user_id,
            intent="pln",
            scope_type=scope_type,
            scope_value=scope_value,
            period_months=period_months,
        )

        # ------------------------------------------------------
        # DETERMINISTIC FALLBACK
        # ------------------------------------------------------

        fallback = PromptManager.pln_text(
            result
        )

        # PLN figures are deterministic database results.  Do not send them
        # to Gemini: a 429/503 must never alter or replace the factual answer.
        return fallback

    # ==========================================================
    # RECTIFIER
    # ==========================================================

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

    # ==========================================================
    # RECTIFIER PROMPT
    # ==========================================================

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

    # ==========================================================
    # AMR
    # ==========================================================

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
                "📡 Daftar Site",
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
                "• Berapa site yang belum AMR "
                "di Kecamatan Waru?\n"
                "• Berapa site yang sudah AMR "
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

    # ==========================================================
    # MAIN ASK
    # ==========================================================

    def ask(
        self,
        question: str,
        user_id=None,
    ) -> str:

        # ------------------------------------------------------
        # USER SESSION
        # ------------------------------------------------------

        self._current_user_id = (
            user_id
            if user_id is not None
            else "default"
        )

        # ------------------------------------------------------
        # INTENT
        # ------------------------------------------------------

        intent = IntentDetector.detect(
            question
        )

        # ------------------------------------------------------
        # ENTITY
        # ------------------------------------------------------

        entity = EntityExtractor.extract(
            question
        )

        # ------------------------------------------------------
        # CONTEXT
        # ------------------------------------------------------

        context = self.conversation.get_context(
            self._current_user_id
        )

        # ------------------------------------------------------
        # FOLLOW-UP CONTEXT
        # ------------------------------------------------------

        if context:

            question_text = (question or "").lower()
            is_new_global_pln_query = (
                intent == "pln"
                and any(phrase in question_text for phrase in (
                    "site mana", "site apa", "semua site", "seluruh site",
                ))
                and not any(phrase in question_text for phrase in (
                    "site mana saja", "site apa saja", "tampilkan semua",
                    "daftar lengkap", "seluruh hasil",
                ))
            )

            # --------------------------------------------------
            # GENERAL FOLLOW-UP
            # --------------------------------------------------

            if intent == "general":

                previous_intent = context.get(
                    "intent"
                )

                if previous_intent:

                    intent = previous_intent

            # --------------------------------------------------
            # SCOPE
            # --------------------------------------------------

            if not entity.scope_type and not is_new_global_pln_query:

                entity.scope_type = context.get(
                    "scope_type"
                )

            # --------------------------------------------------
            # SCOPE VALUE
            # --------------------------------------------------

            if not entity.scope_value and not is_new_global_pln_query:

                entity.scope_value = context.get(
                    "scope_value"
                )

            # --------------------------------------------------
            # SITE ID
            # --------------------------------------------------

            if not entity.site_id:

                entity.site_id = context.get(
                    "site_id"
                )

            # --------------------------------------------------
            # PERIOD
            # --------------------------------------------------

            if not entity.period_months:

                entity.period_months = context.get(
                    "period_months"
                )

        # ======================================================
        # PLN
        # ======================================================

        if intent == "pln":

            return self._handle_pln(
                question,
                entity,
            )

        # ======================================================
        # AMR
        # ======================================================

        if intent == "amr":

            return self._handle_amr(
                question,
                entity,
            )

        # ======================================================
        # RECTIFIER
        # ======================================================

        if intent == "rectifier":

            return self._handle_rectifier(
                question,
                entity,
            )

        # ======================================================
        # OUTAGE
        # ======================================================

        if intent == "outage":

            if (
                not entity.scope_type
                or not entity.scope_value
            ):

                return (
                    "Untuk mencari data pemadaman, "
                    "sebutkan scope yang dimaksud: "
                    "Site, Kecamatan, Kabupaten, "
                    "NOP, atau Cluster.\n\n"
                    "Contoh:\n"
                    "Berapa rata-rata pemadaman "
                    "Kecamatan Taman?"
                )

            result = self.registry.get(
                "outage"
            ).analyze(
                entity.scope_type,
                entity.scope_value,
            )

            if result is None:

                return (
                    f"Data pemadaman tidak ditemukan "
                    f"untuk {entity.scope_type} "
                    f"{entity.scope_value}."
                )

            fallback = (
                PromptManager.outage_text(
                    result
                )
            )

            return self._present(
                PromptManager.outage_prompt(
                    question,
                    result,
                ),
                fallback,
            )

        # ======================================================
        # BATTERY + OUTAGE
        # ======================================================

        if intent == "battery_outage":

            if not entity.site_id:

                return (
                    "Untuk analisis battery dan "
                    "pemadaman sekaligus, sebutkan "
                    "Site ID.\n\n"
                    "Contoh:\n"
                    "Bagaimana kondisi battery "
                    "ABC123 dan pemadamannya?"
                )

            battery = self.registry.get(
                "battery"
            ).analyze_site(
                entity.site_id
            )

            if battery is None:

                return (
                    f"Site {entity.site_id} "
                    "tidak ditemukan."
                )

            outage = self.registry.get(
                "outage"
            ).analyze(
                "siteid",
                entity.site_id,
            )

            if outage is None:

                return (
                    PromptManager.battery_text(
                        battery
                    )
                    + "\n\n"
                    "Data outage site belum tersedia."
                )

            fallback = (
                PromptManager.battery_text(
                    battery
                )
                + "\n\n"
                + PromptManager.outage_text(
                    outage
                )
            )

            return self._present(
                PromptManager.battery_outage_prompt(
                    question,
                    battery,
                    outage,
                ),
                fallback,
            )

        # ======================================================
        # BATTERY
        # ======================================================

        if intent == "battery":

            site_id = entity.site_id

            # --------------------------------------------------
            # PROVINCE
            # --------------------------------------------------

            province = getattr(entity, "province", None)

            text = (
                question
                or ""
            ).lower().strip()

            if not province:
                if "jawa timur" in text or "jatim" in text:
                    province = "Jawa Timur"

            battery_service = self.registry.get(
                "battery"
            )

            if province:

                summary = (
                    battery_service
                    .analyze_province(
                        province
                    )
                )

                if summary is None:
                    return (
                        f"Tidak ditemukan data site "
                        f"untuk Provinsi {province}."
                    )

                return self._present(
                    PromptManager.battery_kabupaten_prompt(
                        question,
                        summary,
                    ),
                    PromptManager.battery_kabupaten_text(
                        summary
                    ),
                )

            kabupaten = (
                entity.kabupaten
                or EntityExtractor.extract_kabupaten(
                    question
                )
            )

            kecamatan = (
                entity.kecamatan
                or EntityExtractor.extract_kecamatan(
                    question
                )
            )

            # --------------------------------------------------
            # KABUPATEN
            # --------------------------------------------------

            if kabupaten:

                summary = (
                    battery_service
                    .analyze_kabupaten(
                        kabupaten
                    )
                )

                if summary is None:
                    return (
                        f"Tidak ditemukan data site "
                        f"untuk Kabupaten {kabupaten}."
                    )

                return self._present(
                    PromptManager.battery_kabupaten_prompt(
                        question,
                        summary,
                    ),
                    PromptManager.battery_kabupaten_text(
                        summary
                    ),
                )

            # --------------------------------------------------
            # KECAMATAN
            # --------------------------------------------------

            if kecamatan:

                summary = (
                    battery_service
                    .analyze_kecamatan(
                        kecamatan
                    )
                )

                if summary is None:
                    return (
                        f"Tidak ditemukan data site "
                        f"untuk Kecamatan {kecamatan}."
                    )

                return self._present(
                    PromptManager.battery_kabupaten_prompt(
                        question,
                        summary,
                    ),
                    PromptManager.battery_kabupaten_text(
                        summary
                    ),
                )

            # --------------------------------------------------
            # SITE
            # --------------------------------------------------

            if site_id is None:

                return (
                    "Silakan sebutkan Site ID, "
                    "Kecamatan, Kabupaten, atau Provinsi.\n\n"
                    "Contoh:\n"
                    "• Bagaimana kondisi battery ABC123?\n"
                    "• Bagaimana kondisi battery Kecamatan Waru?\n"
                    "• Bagaimana kondisi battery Kabupaten Sidoarjo?\n"
                    "• Bagaimana kondisi battery Jawa Timur?"
                )

            result = (
                battery_service
                .analyze_site(
                    site_id
                )
            )

            if result is None:

                return (
                    f"Site {site_id} "
                    "tidak ditemukan."
                )

            return self._present(
                PromptManager.battery_prompt(
                    question,
                    result,
                ),
                PromptManager.battery_text(
                    result
                ),
            )

        # ======================================================
        # EXISTING MASTER SITE QUERY
        # ======================================================

        factual_answer = (
            self.data_query.execute(
                question
            )
        )

        if factual_answer is not None:

            return self._present(
                PromptManager.data_query_prompt(
                    question,
                    factual_answer,
                ),
                factual_answer,
            )

        # ======================================================
        # GENERAL
        # ======================================================

        return self._present(
            PromptManager.general_prompt(
                question
            ),
            (
                "Layanan AI tidak tersedia. "
                "Silakan periksa konfigurasi Gemini."
            ),
        )

    _PLN_MONTHS = {
        "januari": 1, "februari": 2, "maret": 3, "april": 4,
        "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
        "september": 9, "oktober": 10, "november": 11, "desember": 12,
    }

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
            # NOP monthly data is scoped through master_site.nop_name by the
            # repository join.  Default to the completed calendar month.
            from datetime import date

            today = date.today()
            previous_month = today.month - 1 or 12
            previous_year = today.year - 1 if today.month == 1 else today.year
            periods = [(previous_year, previous_month)]
        # A rolling request may use PLNService; an explicit calendar month may
        # never silently fall back to the latest available month.
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
