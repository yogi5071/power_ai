from dataclasses import dataclass, field
from typing import Any

from models.intent import Intent


@dataclass
class RouterResult:

    intent: Intent

    confidence: float

    original_text: str

    normalized_text: str

    entities: dict[str, Any] = field(default_factory=dict)