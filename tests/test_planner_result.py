from planner.planner_result import PlannerResult
from models.execution_plan import ExecutionPlan

plan = ExecutionPlan(
    module="battery",
    operation="count"
)

result = PlannerResult.ok(plan)

print(result.success)
print(result.plan.module)