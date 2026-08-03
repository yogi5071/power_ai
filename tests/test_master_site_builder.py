from planner.execution_plan_parser import ExecutionPlanParser
from planner.validator import ExecutionPlanValidator
from query.builders.master_site_builder import MasterSiteBuilder

json_data = {
    "module": "battery",
    "operation": "list",
    "select": [
        "site_id",
        "site_name",
        "umur_battery"
    ],
    "filters": [
        {
            "field": "jenis_battery",
            "operator": "=",
            "value": "aki"
        }
    ],
    "group_by": [],
    "order_by": [
        {
            "field": "umur_battery",
            "direction": "desc"
        }
    ],
    "limit": 100,
    "description": "Battery VRLA"
}

plan = ExecutionPlanParser.parse(json_data)

ExecutionPlanValidator.validate(plan)

sql = MasterSiteBuilder.build(plan)

print(sql)