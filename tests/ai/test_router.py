from power_engine.ai.ai_router import AIRouter


router = AIRouter()

reply = router.ask(

    "Bagaimana kondisi battery site SBY001?"

)

print(reply)