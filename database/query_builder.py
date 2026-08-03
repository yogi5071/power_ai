class QueryBuilder:

    @staticmethod
    def build_where(filters):

        if not filters:
            return "", []

        clauses = []

        params = []

        for f in filters:

            column = f["field"]

            operator = f["operator"]

            value = f["value"]

            clauses.append(
                f"{column} {operator} %s"
            )

            params.append(value)

        where = " WHERE " + " AND ".join(clauses)

        return where, params