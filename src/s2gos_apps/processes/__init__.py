from s2gos_apps.registry import registry

from . import frascati, gobabeb, kairouan, pisa, pnp
from .common import generation, simulation

__all__ = [
    "registry",
    "frascati",
    "gobabeb",
    "kairouan",
    "pisa",
    "pnp",
    "generation",
    "simulation",
]
