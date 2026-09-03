"""
Prompt Manager
Power AI Copilot
"""


class PromptManager:

    # ==========================================================
    # BATTERY TEXT
    # ==========================================================

    @staticmethod
    def battery_text(explanation):

        return (
            f"Battery Health Summary\n\n"
            f"Site ID            : "
            f"{explanation.site.siteid}\n"
            f"Health Status      : "
            f"{explanation.health_status}\n"
            f"Severity           : "
            f"{explanation.severity}\n"
            f"Health Score       : "
            f"{explanation.health_score}/100\n\n"
            f"Battery Information\n"
            f"- Technology       : "
            f"{explanation.technology}\n"
            f"- Battery Age      : "
            f"{explanation.battery_age} Tahun\n"
            f"- Warranty         : "
            f"{explanation.warranty}\n"
            f"- Remaining Backup : "
            f"{explanation.remaining_time:.2f} Jam\n\n"
            f"Recommendation\n"
            f"{explanation.recommendation}"
        )

    # ==========================================================
    # BATTERY KABUPATEN
    # ==========================================================

    @staticmethod
    def battery_kabupaten_text(summary):

        priority = "\n\n".join(
            (
                f"{site['site_id']} "
                f"({site['site_name']})\n"
                f"Health Status : "
                f"{site['health_status']}\n"
                f"Severity      : "
                f"{site['severity']}\n"
                f"Health Score  : "
                f"{site['health_score']}/100"
            )
            for site in summary["priority_sites"]
        ) or "Tidak ada site prioritas."

        technology = "\n".join(
            f"- {name:<8}: {count} Site"
            for name, count
            in summary["technology"].items()
        ) or "- Tidak ada data"

        return (
            f"Battery Health Summary\n\n"
            f"{summary['location_type']} : "
            f"{summary['location_name']}\n\n"
            f"Total Site            : "
            f"{summary['total_sites']}\n"
            f"Average Health Score  : "
            f"{summary['average_health_score']}/100\n\n"
            f"Health Distribution\n"
            f"- HEALTH : "
            f"{summary['health_count']} Site\n"
            f"- WARNING : "
            f"{summary['warning_count']} Site\n"
            f"- BAD : "
            f"{summary['bad_count']} Site\n\n"
            f"Battery Technology\n"
            f"{technology}\n\n"
            f"Priority Inspection Site\n"
            f"{priority}"
        )

    # ==========================================================
    # OUTAGE TEXT
    # ==========================================================

    @staticmethod
    def outage_text(result):

        return (
            "Outage Engineering Summary\n\n"
            f"Scope       : "
            f"{result.scope_type} "
            f"{result.scope_value}\n"
            f"Total Site  : "
            f"{result.total_site}\n\n"
            f"Pemadaman Minimum : "
            f"{PromptManager._decimal(result.minimum)} "
            f"kali/bulan\n"
            f"Pemadaman Average  : "
            f"{PromptManager._decimal(result.average)} "
            f"kali/bulan\n"
            f"Pemadaman Maximum : "
            f"{PromptManager._decimal(result.maximum)} "
            f"kali/bulan"
        )

    # ==========================================================
    # PLN TEXT
    #
    # DEFAULT:
    #   Hanya average per site.
    #
    # TOTAL:
    #   Hanya dimasukkan jika include_total=True.
    #
    # HISTORICAL:
    #   Seluruh perubahan antarperiode dimasukkan.
    #
    # Gemini hanya membaca hasil Power Engine.
    # ==========================================================

    @staticmethod
    def pln_text(
        result,
        include_total=False,
    ):

        lines = []

        # ======================================================
        # MONTHLY AVERAGE PER SITE
        # ======================================================

        for item in result.available_months:

            average_value = item.get(
                "average_value"
            )

            if average_value is None:

                lines.append(
                    f"- {item['month_name']} "
                    f"{item['year']}: "
                    f"Data belum tersedia"
                )

            else:

                lines.append(
                    f"- {item['month_name']} "
                    f"{item['year']}: "
                    f"Average/site Rp "
                    f"{int(average_value):,}"
                    .replace(",", ".")
                )

        # ======================================================
        # BASE TEXT
        # ======================================================

        text = (
            "PLN Monthly Analysis\n\n"
            f"Scope : "
            f"{result.scope_type} "
            f"{result.scope_value}\n"
            f"Site dengan data : "
            f"{result.site_count}\n\n"
            + "\n".join(lines)
        )

        # ======================================================
        # AVERAGE PERIODE
        #
        # Ini adalah average tagihan per site
        # sepanjang periode.
        # ======================================================

        if result.average is not None:

            text += (
                "\n\n"
                f"Average tagihan per site "
                f"selama periode : "
                f"Rp {int(result.average):,}"
                .replace(",", ".")
            )

        # ======================================================
        # HISTORICAL TREND
        #
        # Semua pasangan periode ditampilkan.
        #
        # Contoh:
        #
        # Juni -> Juli
        # Juli -> Agustus
        #
        # Tidak hanya latest vs previous.
        # ======================================================

        trend_changes = result.trend_changes

        if trend_changes:

            text += (
                "\n\n"
                "Historical Trend\n"
            )

            for change in trend_changes:

                from_month = change["from"]
                to_month = change["to"]

                from_average = (
                    change["from_average"]
                )

                to_average = (
                    change["to_average"]
                )

                direction = (
                    change["direction"]
                )

                percentage = (
                    change["percentage_change"]
                )

                text += (
                    f"- "
                    f"{from_month['month_name']} "
                    f"{from_month['year']} "
                    f"→ "
                    f"{to_month['month_name']} "
                    f"{to_month['year']} : "
                    f"{direction}"
                )

                if (
                    from_average is not None
                    and to_average is not None
                ):

                    text += (
                        f" | "
                        f"Rp {int(from_average):,}"
                        .replace(",", ".")
                        +
                        f" → "
                        f"Rp {int(to_average):,}"
                        .replace(",", ".")
                    )

                if percentage is not None:

                    text += (
                        f" "
                        f"({abs(float(percentage)):.2f}%)"
                    )

                text += "\n"

        # ======================================================
        # TREND SUMMARY
        # ======================================================

        if result.has_trend:

            if result.trend_label is not None:

                text += (
                    "\n"
                    "Trend Pattern : "
                    f"{result.trend_label}"
                )

            if result.overall_trend is not None:

                text += (
                    "\n"
                    "Overall Trend : "
                    f"{result.overall_trend}"
                )

            if (
                result.overall_change_percentage
                is not None
            ):

                overall_direction = (
                    "naik"
                    if result.overall_change_percentage > 0
                    else "turun"
                    if result.overall_change_percentage < 0
                    else "tetap"
                )

                text += (
                    "\n"
                    f"Perubahan awal-akhir : "
                    f"{overall_direction} "
                    f"({abs(float(result.overall_change_percentage)):.2f}%)"
                )

        # ======================================================
        # TOTAL
        #
        # HANYA JIKA USER MEMINTA TOTAL.
        # ======================================================

        if include_total:

            text += (
                "\n\n"
                f"Total periode : "
                f"Rp {int(result.total):,}"
                .replace(",", ".")
            )

        # ======================================================
        # CAPACITY
        # ======================================================

        if result.has_capacity:

            text += (
                "\n"
                f"Kapasitas PLN : "
                f"{result.kapasitas_pln} VA"
            )

        return text

    # ==========================================================
    # OUTAGE PROMPT
    # ==========================================================

    @staticmethod
    def outage_prompt(
        question,
        result,
    ):

        return f"""
Kamu adalah Power AI Copilot untuk Power Operation.

Jawab berdasarkan data engineering outage berikut.

{PromptManager.outage_text(result)}

Pertanyaan user:
{question}

Instruksi:
- Gunakan hanya data di atas.
- Jangan mengubah angka.
- Jangan menghitung ulang min/avg/max.
- Jelaskan bahwa data outage adalah hasil analisis engineering.
- Jangan memasukkan outage ke Health Score.
- Gunakan Bahasa Indonesia profesional dan ringkas.
"""

    # ==========================================================
    # PLN PROMPT
    #
    # Gemini bertugas memberikan INSIGHT.
    #
    # Power Engine bertugas:
    # - query database
    # - average
    # - percentage
    # - trend
    # - overall trend
    #
    # Gemini TIDAK menjadi kalkulator.
    # ==========================================================

    @staticmethod
    def pln_prompt(
        question,
        result,
        include_total=False,
    ):

        factual_data = (
            PromptManager.pln_text(
                result,
                include_total=include_total,
            )
        )

        return f"""
Kamu adalah Power AI Copilot untuk Power Operation.

Tugas utama kamu adalah menjelaskan kondisi dan pola
tagihan PLN berdasarkan data engineering yang diberikan.

DATA PLN:
{factual_data}

PERTANYAAN USER:
{question}

==========================================================
ATURAN DATA
==========================================================

1. Gunakan HANYA data PLN yang tersedia di atas.

2. Jangan membuat angka, bulan, tahun, site count,
   atau nilai rupiah yang tidak tersedia.

3. Jangan mengubah nilai tagihan.

4. Jangan menghitung ulang nilai bulanan.

5. Jangan menghitung ulang average.

6. Average yang diberikan Power Engine adalah
   average tagihan per site.

7. Jangan mengubah average per site menjadi total.

8. Jangan menyebut average sebagai total.

9. Jangan menyebut total sebagai average.

==========================================================
ATURAN TOTAL
==========================================================

10. Total periode TIDAK BOLEH ditampilkan secara default.

11. Total periode hanya boleh disebutkan jika user
    secara eksplisit meminta:

    - total
    - jumlah keseluruhan
    - akumulasi
    - berapa semuanya
    - berapa seluruh tagihan
    - total tagihan
    - jumlah tagihan keseluruhan

    atau kalimat lain yang memiliki makna sama.

12. Jika user tidak meminta total:

    JANGAN menampilkan:
    "Total periode"

    JANGAN menghitung total sendiri.

    JANGAN menyebutkan total meskipun secara matematis
    dapat dihitung dari data.

==========================================================
ATURAN TREND
==========================================================

13. Semua perubahan trend yang terdapat pada DATA PLN
    sudah dihitung oleh Power Engine.

14. Jangan menghitung ulang persentase perubahan.

15. Gunakan Historical Trend sebagai sumber utama
    untuk menjelaskan perubahan antarperiode.

16. Gunakan Trend Pattern untuk menjelaskan pola
    keseluruhan antarbulan.

17. Gunakan Overall Trend untuk menjelaskan posisi
    periode terakhir dibanding periode pertama.

18. Bedakan:

    Trend Pattern
    = pola perubahan antarperiode.

    Overall Trend
    = posisi periode terakhir dibanding periode pertama.

19. Jangan menyebut trend "konsisten naik" jika pola
    menunjukkan naik → turun atau turun → naik.

20. Jika pola berubah arah, gunakan istilah yang sesuai
    dengan data seperti:

    - fluktuatif
    - mengalami perubahan arah
    - turun kemudian naik
    - naik kemudian turun

==========================================================
ATURAN PERIODE
==========================================================

21. Jika hanya 1 bulan:

    - tampilkan average bulan tersebut.
    - jangan membuat analisis trend.
    - jelaskan kondisi bulan tersebut saja.

22. Jika 2 bulan:

    - bandingkan kedua bulan.
    - jelaskan naik, turun, atau tetap.
    - gunakan perubahan yang sudah dihitung Engine.

23. Jika 3 bulan:

    - gunakan seluruh Historical Trend.
    - identifikasi pola antarbulan.
    - jelaskan posisi awal dibanding akhir.

24. Jika 4 bulan atau lebih:

    - gunakan seluruh Historical Trend.
    - jangan hanya menggunakan dua bulan terakhir.
    - identifikasi perubahan arah.
    - identifikasi pola dominan jika memang terlihat.
    - jelaskan perubahan awal sampai akhir.
    - jangan memaksakan kesimpulan.

==========================================================
ATURAN INSIGHT
==========================================================

25. Insight harus berasal langsung dari data.

26. Jangan membuat hubungan sebab-akibat.

27. Jangan mengatakan kenaikan tagihan disebabkan oleh:

    - kenaikan beban
    - konsumsi energi
    - tarif PLN
    - jam operasi
    - perangkat
    - power factor
    - atau faktor lainnya

    kecuali faktor tersebut memang tersedia dalam data.

28. Jangan menganggap kenaikan tagihan otomatis berarti
    konsumsi listrik meningkat.

29. Jika data tidak cukup untuk menyimpulkan sesuatu,
    katakan bahwa data belum cukup.

30. Jangan membuat insight generik yang tidak berhubungan
    dengan angka.

31. Insight harus menjawab pertanyaan user.

==========================================================
FORMAT JAWABAN
==========================================================

32. Untuk pertanyaan historical:

    Rincian PLN:

    - Bulan Tahun: Average/site Rp ...

33. Jika relevan:

    Average periode: Rp ...

34. Jika tersedia minimal 2 periode:

    Insight:
    Jelaskan perubahan dan pola berdasarkan
    Historical Trend.

35. Jika tersedia 3 bulan atau lebih dan terjadi
    perubahan arah, jelaskan perubahan arah tersebut.

36. Jika user meminta TOTAL secara eksplisit:

    Total periode: Rp ...

37. Jika user tidak meminta TOTAL:

    JANGAN tampilkan "Total periode".

38. Gunakan Bahasa Indonesia profesional,
    natural, dan ringkas.

39. Jangan mengulang pertanyaan user.

40. Jangan menambahkan disclaimer yang tidak diperlukan.

41. Jangan mengatakan "berdasarkan data yang tersedia"
    berulang-ulang jika jawabannya sudah jelas.

42. Fokus pada jawaban yang benar-benar menjawab
    pertanyaan user.
"""

    # ==========================================================
    # BATTERY + OUTAGE
    # ==========================================================

    @staticmethod
    def battery_outage_prompt(
        question,
        battery_result,
        outage_result,
    ):

        return f"""
Kamu adalah Power AI Copilot dan Senior Power Operation Engineer.

Data Battery:
{PromptManager.battery_text(battery_result)}

Data Outage Engineering:
{PromptManager.outage_text(outage_result)}

Pertanyaan:
{question}

Instruksi:
- Gunakan hanya data engineering di atas.
- Jangan mengubah Health Score.
- Outage adalah contextual information dan bukan
  komponen Health Score.
- Jangan menghitung ulang data.
- Jelaskan hubungan hanya jika didukung data yang tersedia.
- Jangan menyatakan sebab-akibat tanpa bukti.
- Gunakan Bahasa Indonesia profesional.
"""

    # ==========================================================
    # GENERAL
    # ==========================================================

    @staticmethod
    def general_prompt(question):

        return f"""
Kamu adalah Power AI Copilot.

Jawablah menggunakan Bahasa Indonesia yang profesional,
jelas, singkat, dan mudah dipahami.

Pertanyaan:
{question}
"""

    # ==========================================================
    # BATTERY PROMPT
    # ==========================================================

    @staticmethod
    def battery_prompt(
        question,
        explanation,
    ):

        reasons = "\n".join(
            f"- {reason}"
            for reason
            in explanation.health_reasons
        ) or "- Tidak ada"

        return f"""
Kamu adalah Power AI Copilot yang berperan sebagai
Senior Power Operation Engineer.

Jawablah berdasarkan data engineering berikut.

Battery Information
Technology       : {explanation.technology}
Battery Age      : {explanation.battery_age} Tahun
Warranty         : {explanation.warranty}
Remaining Backup : {explanation.remaining_time:.2f} Jam

Health Assessment
Health Status    : {explanation.health_status}
Severity         : {explanation.severity}
Health Score     : {explanation.health_score}/100

Health Score Reasons
{reasons}

Recommendation
{explanation.recommendation}

Technical Conclusion
{explanation.conclusion}

Pertanyaan User
{question}

Instruksi:
- Gunakan hanya data engineering di atas.
- Jangan mengubah angka.
- Jangan menghitung ulang.
- Jangan membuat asumsi.
- Jangan mengubah satuan Remaining Backup dari JAM.
"""

    # ==========================================================
    # DATA QUERY
    # ==========================================================

    @staticmethod
    def data_query_prompt(
        question,
        factual_answer,
    ):

        return f"""
Kamu adalah Power AI Copilot.

Jawablah pertanyaan user berdasarkan data hasil query
database berikut.

{factual_answer}

Pertanyaan User:
{question}

Instruksi:
- Jangan mengubah angka.
- Jangan menghitung ulang.
- Jangan menambahkan data yang tidak tersedia.
- Gunakan hanya data hasil query.
- Jangan mengarang informasi.
"""

    # ==========================================================
    # ALARM
    # ==========================================================

    @staticmethod
    def alarm_prompt(question):

        return PromptManager.general_prompt(
            question
        )

    # ==========================================================
    # BATTERY KABUPATEN PROMPT
    # ==========================================================

    @staticmethod
    def battery_kabupaten_prompt(
        question,
        summary,
    ):

        return f"""
Kamu adalah Power AI Copilot.

Tugasmu HANYA merapikan keluaran Power Engine.
Jangan mengubah angka atau Health Score.

{PromptManager.battery_kabupaten_text(summary)}

Pertanyaan User:
{question}
"""

    # ==========================================================
    # DECIMAL
    # ==========================================================

    @staticmethod
    def _decimal(value):

        if value is None:

            return "-"

        return (
            f"{float(value):.2f}"
            .rstrip("0")
            .rstrip(".")
            .replace(".", ",")
        )