# needs registry to be initialized first.
# might be good to have it work as a singleton?
from s2gos_apps.registry import registry

from . import (
    frascati, 
    gobabeb, 
    kairouan, 
    pisa, 
    pnp
)
from .common import (
    generation, 
    simulation
)

