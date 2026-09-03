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
        # DIRECT PLN MONTHLY QUERY
        #
        # Pertanyaan faktual KWH/RPTAG untuk site dan bulan
        # dijawab langsung dari repository PLN tanpa Gemini.
        # ======================================================

        month_map = {
            "januari": "januari",
            "februari": "februari",
            "maret": "maret",
            "april": "april",
            "mei": "mei",
            "juni": "juni",
            "juli": "juli",
            "agustus": "agustus",
            "september": "september",
            "oktober": "oktober",
            "november": "november",
            "desember": "desember",
        }

        requested_month = next(
            (
                month
                for month in month_map
                if month in text
            ),
            None,
        )

        asking_kwh = (
            "kwh" in text
            or "kwh-nya" in text
            or "pemakaian listrik" in text
        )

        asking_rptag = (
            "rptag" in text
            or "rp tag" in text
            or "tagihan" in text
        )

        if (
            requested_month
            and scope_type == "siteid"
            and scope_value
            and (asking_kwh or asking_rptag)
        ):

            monthly_repository = getattr(
                pln_service,
                "repository",
                None,
            )

            site_data = None

            if monthly_repository is not None:
                try:
                    site_data = monthly_repository.get_site_data(
                        scope_value
                    )
                except Exception:
                    site_data = None

            if site_data:

                year = site_data.get("tahun")
                kwh_value = site_data.get(
                    f"kwh_{requested_month}"
                )
                rptag_value = site_data.get(
                    f"rptag_{requested_month}"
                )

                month_name = requested_month.capitalize()

                if (
                    kwh_value is None
                    and rptag_value is None
                ):
                    return (
                        f"Data KWH/RPTAG site "
                        f"{scope_value} bulan "
                        f"{month_name} belum tersedia."
                    )

                if asking_kwh and asking_rptag:

                    kwh_text = (
                        f"{float(kwh_value):,.0f} kWh"
                        .replace(",", ".")
                        if kwh_value is not None
                        else "-"
                    )

                    rptag_text = (
                        f"Rp {int(rptag_value):,}"
                        .replace(",", ".")
                        if rptag_value is not None
                        else "-"
                    )

                    return (
                        "⚡ PLN MONTHLY\n\n"
                        f"Site ID : {scope_value}\n"
                        f"Bulan   : {month_name} {year or ''}\n"
                        f"KWH     : {kwh_text}\n"
                        f"RPTAG   : {rptag_text}"
                    )

                if asking_kwh:

                    if kwh_value is None:
                        return (
                            f"Data KWH site {scope_value} "
                            f"bulan {month_name} "
                            "belum tersedia."
                        )

                    return (
                        "⚡ KWH PLN\n\n"
                        f"Site ID : {scope_value}\n"
                        f"Bulan   : {month_name} {year or ''}\n"
                        f"KWH     : "
                        f"{float(kwh_value):,.0f} kWh"
                        .replace(",", ".")
                    )

                if asking_rptag:

                    if rptag_value is None:
                        return (
                            f"Data RPTAG site {scope_value} "
                            f"bulan {month_name} "
                            "belum tersedia."
                        )

                    return (
                        "⚡ RPTAG PLN\n\n"
                        f"Site ID : {scope_value}\n"
                        f"Bulan   : {month_name} {year or ''}\n"
                        f"RPTAG   : Rp "
                        f"{int(rptag_value):,}"
                        .replace(",", ".")
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

        # ------------------------------------------------------
        # AI PRESENTATION
        # ------------------------------------------------------

        return self._present(
            PromptManager.pln_prompt(
                question,
                result,
            ),
            fallback,
        )

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

            if not entity.scope_type:

                entity.scope_type = context.get(
                    "scope_type"
                )

            # --------------------------------------------------
            # SCOPE VALUE
            # --------------------------------------------------

            if not entity.scope_value:

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