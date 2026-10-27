import unittest

from database.site_pln_contract_repository import SitePLNContractRepository


class ContractScopeTests(unittest.TestCase):
    def test_explicit_city_matches_city_prefix_only(self):
        clause, params = SitePLNContractRepository.build_scope_filter("kota", "Mojokerto")
        self.assertIn("CONCAT('kota '", clause)
        self.assertNotIn("kabupaten '", clause)
        self.assertEqual(params, ("Mojokerto",))

    def test_explicit_kabupaten_accepts_bare_or_prefixed_value(self):
        clause, params = SitePLNContractRepository.build_scope_filter("kabupaten", "Mojokerto")
        self.assertIn("CONCAT('kabupaten '", clause)
        self.assertEqual(params, ("Mojokerto", "Mojokerto"))

    def test_bare_name_matches_both_city_and_kabupaten(self):
        clause, params = SitePLNContractRepository.build_scope_filter(
            "city_or_kabupaten", "Mojokerto"
        )
        self.assertIn("CONCAT('kota '", clause)
        self.assertIn("CONCAT('kabupaten '", clause)
        self.assertEqual(params, ("Mojokerto",) * 3)

    def test_scope_values_remain_bound_parameters(self):
        clause, params = SitePLNContractRepository.build_scope_filter(
            "city_or_kabupaten", "X' OR 1=1 --"
        )
        self.assertNotIn("X' OR 1=1", clause)
        self.assertEqual(params, ("X' OR 1=1 --",) * 3)

    def test_unknown_scope_is_rejected(self):
        with self.assertRaises(ValueError):
            SitePLNContractRepository.build_scope_filter("unknown", "Mojokerto")

    def test_count_query_uses_ambiguous_scope_clause_and_bound_values(self):
        class Cursor:
            query = None
            params = None
            def execute(self, query, params):
                self.query, self.params = query, params
            def fetchone(self):
                return {"total_site": 2}
            def close(self):
                pass

        repo = object.__new__(SitePLNContractRepository)
        cursor = Cursor()
        repo.get_cursor = lambda: cursor

        self.assertEqual(repo.count_sites("city_or_kabupaten", "Mojokerto"), 2)
        self.assertIn("CONCAT('kota '", cursor.query)
        self.assertIn("CONCAT('kabupaten '", cursor.query)
        self.assertEqual(cursor.params, ("Mojokerto",) * 3)


if __name__ == "__main__":
    unittest.main()
