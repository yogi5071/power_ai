"""
planner/planner_result.py

Planner result model.

Planner tidak langsung mengembalikan
ExecutionPlan, tetapi dibungkus dalam
PlannerResult agar dapat membawa
status, pesan, dan error.
"""

from dataclasses import dataclass, field
from typing import Optional

from models.execution_plan import ExecutionPlan


@dataclass
class PlannerResult:
    """
    Hasil akhir Planner.
    """

    # Planner berhasil?
    success: bool

    # Execution Plan
    plan: Optional[ExecutionPlan] = None

    # Pesan untuk user
    message: str = ""

    # Error internal
    error: str = ""

    # Apakah perlu klarifikasi user?
    need_clarification: bool = False

    # Pertanyaan klarifikasi
    clarification_question: Optional[str] = None

    # Informasi tambahan
    metadata: dict = field(default_factory=dict)

    @classmethod
    def ok(
        cls,
        plan: ExecutionPlan,
        message: str = ""
    ):
        """
        Planner berhasil.
        """

        return cls(
            success=True,
            plan=plan,
            message=message
        )

    @classmethod
    def fail(
        cls,
        error: str,
        message: str = ""
    ):
        """
        Planner gagal.
        """

        return cls(
            success=False,
            error=error,
            message=message
        )

    @classmethod
    def clarification(
        cls,
        question: str
    ):
        """
        Planner membutuhkan
        informasi tambahan.
        """

        return cls(
            success=False,
            need_clarification=True,
            clarification_question=question
        )