from planner.execution_plan_parser import ExecutionPlanParser

json_response = {
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
            "value": "VRLA"
        }
    ],
    "group_by": [],
    "order_by": [
        {
            "field": "umur_battery",
            "direction": "DESC"
        }
    ],
    "limit": 100,
    "description": "List battery VRLA"
}

plan = ExecutionPlanParser.parse(json_response)

print("=== ExecutionPlan ===")
print(plan)

print("\n=== Module ===")
print(plan.module)

print("\n=== Operation ===")
print(plan.operation)

print("\n=== Select ===")
print(plan.select)

print("\n=== Filters ===")
for f in plan.filters:
    print(f)

print("\n=== Order By ===")
for s in plan.order_by:
    print(s)

print("\n=== Limit ===")
print(plan.limit)

print("\n=== Description ===")
print(plan.description)