from models.execution_plan import ExecutionPlan


plan = ExecutionPlan(

    module="battery",

    operation="summary"

)


plan.add_filter(

    "kabupaten",

    "=",

    "Probolinggo"

)


print(plan)

print(
    plan.has_filter(
        "kabupaten"
    )
)