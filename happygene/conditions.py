"""Environmental conditions for expression models."""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Conditions:
    """Environmental conditions affecting gene expression.

    Parameters
    ----------
    tf_concentration : float
        Transcription factor concentration (default: 0.0)
    temperature : float
        Environmental temperature in Celsius (default: 37.0)
    nutrients : float
        Nutrient availability (default: 1.0, range 0-1)
    extra : dict
        Additional condition parameters (extensible)
    """

    tf_concentration: float = 0.0
    temperature: float = 37.0
    nutrients: float = 1.0
    extra: Dict[str, Any] = field(default_factory=dict)
