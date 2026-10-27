"""Metadata for site_pln_monthly."""

from metadata.base import FieldMetadata, TableMetadata


SITE_PLN_MONTHLY = TableMetadata(
    table_name="site_pln_monthly",
    primary_key="siteid",
    description="Monthly PLN billing by site and year.",
    fields={
        "site_id": FieldMetadata(
            name="site_id", label="Site ID", column="siteid",
            data_type="string", operators=["=", "LIKE", "IN"],
            description="Site ID linked to master_site",
        ),
        "tahun": FieldMetadata(
            name="tahun", label="Tahun", column="tahun",
            data_type="number", operators=["=", ">", "<", ">=", "<=", "BETWEEN"],
            description="Billing year",
        ),
        "pln_januari": FieldMetadata(name="pln_januari", label="PLN Januari", column="pln_januari", data_type="number", unit="rupiah"),
        "pln_februari": FieldMetadata(name="pln_februari", label="PLN Februari", column="pln_februari", data_type="number", unit="rupiah"),
        "pln_maret": FieldMetadata(name="pln_maret", label="PLN Maret", column="pln_maret", data_type="number", unit="rupiah"),
        "pln_april": FieldMetadata(name="pln_april", label="PLN April", column="pln_april", data_type="number", unit="rupiah"),
        "pln_mei": FieldMetadata(name="pln_mei", label="PLN Mei", column="pln_mei", data_type="number", unit="rupiah"),
        "pln_juni": FieldMetadata(name="pln_juni", label="PLN Juni", column="pln_juni", data_type="number", unit="rupiah"),
        "pln_juli": FieldMetadata(name="pln_juli", label="PLN Juli", column="pln_juli", data_type="number", unit="rupiah"),
        "pln_agustus": FieldMetadata(name="pln_agustus", label="PLN Agustus", column="pln_agustus", data_type="number", unit="rupiah"),
        "pln_september": FieldMetadata(name="pln_september", label="PLN September", column="pln_september", data_type="number", unit="rupiah"),
        "pln_oktober": FieldMetadata(name="pln_oktober", label="PLN Oktober", column="pln_oktober", data_type="number", unit="rupiah"),
        "pln_november": FieldMetadata(name="pln_november", label="PLN November", column="pln_november", data_type="number", unit="rupiah"),
        "pln_desember": FieldMetadata(name="pln_desember", label="PLN Desember", column="pln_desember", data_type="number", unit="rupiah"),
    },
)
