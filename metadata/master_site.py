"""
metadata/master_site.py

Business metadata for master_site table.
"""

from metadata.base import FieldMetadata, TableMetadata


MASTER_SITE = TableMetadata(

    table_name="master_site",

    primary_key="siteid",

    description="Master information for every power site.",

    fields={

        # ==========================================================
        # SITE INFORMATION
        # ==========================================================

        "site_id": FieldMetadata(
            name="site_id",
            label="Site ID",
            column="siteid",
            data_type="string",
            operators=["=", "LIKE", "IN"],
            description="Unique Site ID"
        ),

        "site_name": FieldMetadata(
            name="site_name",
            label="Site Name",
            column="site_name",
            data_type="string",
            operators=["=", "LIKE"],
            description="Site Name"
        ),

        "kabupaten": FieldMetadata(
            name="kabupaten",
            label="Kabupaten",
            column="kabupaten",
            data_type="string",
            operators=["=", "LIKE", "IN"],
            description="Kabupaten"
        ),

        "kecamatan": FieldMetadata(
            name="kecamatan",
            label="Kecamatan",
            column="kecamatan",
            data_type="string",
            operators=["=", "LIKE", "IN"],
            description="Kecamatan"
        ),

        "cluster": FieldMetadata(
            name="cluster",
            label="Cluster",
            column="cluster",
            data_type="string",
            operators=["=", "LIKE", "IN"],
            description="Cluster"
        ),

        "nop": FieldMetadata(
            name="nop",
            label="NOP",
            column="nop_name",
            data_type="string",
            operators=["=", "LIKE", "IN"],
            description="NOP Name"
        ),

        # ==========================================================
        # BATTERY
        # ==========================================================

        "jenis_battery": FieldMetadata(
            name="jenis_battery",
            label="Jenis Battery",
            column="battery",
            data_type="enum",
            operators=["=", "IN"],
            values=[
                "VRLA",
                "Lithium"
            ],
            aliases={
                "VRLA": [
                    "vrla",
                    "aki",
                    "aki vrla",
                    "lead acid",
                    "lead-acid"
                ],
                "Lithium": [
                    "lithium",
                    "li",
                    "li ion",
                    "li-ion"
                ]
            },
            description="Battery Technology"
        ),

        "umur_battery": FieldMetadata(
            name="umur_battery",
            label="Umur Battery",
            column="umur_battery_tahun",
            data_type="number",
            operators=[
                "=",
                ">",
                "<",
                ">=",
                "<=",
                "BETWEEN"
            ],
            unit="tahun",
            description="Battery Age"
        ),

        "kategori_umur": FieldMetadata(
            name="kategori_umur",
            label="Kategori Umur Battery",
            column="kategori_umur_battery",
            data_type="string",
            operators=[
                "=",
                "IN"
            ],
            description="Battery Age Category"
        ),

        "status_warranty": FieldMetadata(
            name="status_warranty",
            label="Warranty",
            column="status_warranty_battery",
            data_type="string",
            operators=[
                "=",
                "IN"
            ],
            description="Battery Warranty Status"
        ),

        "total_bank": FieldMetadata(
            name="total_bank",
            label="Total Bank",
            column="total_bank",
            data_type="number",
            operators=[
                "=",
                ">",
                "<",
                ">=",
                "<="
            ],
            description="Total Battery Bank"
        ),

        "total_vrla": FieldMetadata(
            name="total_vrla",
            label="Total VRLA",
            column="total_vrla",
            data_type="number",
            operators=[
                "=",
                ">",
                "<",
                ">=",
                "<="
            ],
            description="Total VRLA Bank"
        ),

        "total_lithium": FieldMetadata(
            name="total_lithium",
            label="Total Lithium",
            column="total_lithium",
            data_type="number",
            operators=[
                "=",
                ">",
                "<",
                ">=",
                "<="
            ],
            description="Total Lithium Bank"
        ),

        # ==========================================================
        # RECTIFIER
        # ==========================================================

        "kategori_rectifier": FieldMetadata(
            name="kategori_rectifier",
            label="Kategori Rectifier",
            column="kategori_rectifier",
            data_type="string",
            operators=[
                "=",
                "IN"
            ],
            description="Rectifier Category"
        ),

        "jumlah_rectifier": FieldMetadata(
            name="jumlah_rectifier",
            label="Jumlah Rectifier",
            column="jumlah_rectifier",
            data_type="number",
            operators=[
                "=",
                ">",
                "<",
                ">=",
                "<="
            ],
            description="Total Rectifier"
        ),

        "jumlah_modul": FieldMetadata(
            name="jumlah_modul",
            label="Jumlah Modul",
            column="jumlah_modul",
            data_type="number",
            operators=[
                "=",
                ">",
                "<",
                ">=",
                "<="
            ],
            description="Total Rectifier Module"
        )

    }

)