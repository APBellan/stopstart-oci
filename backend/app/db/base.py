from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base do SQLAlchemy para todas as tabelas."""
    pass


# IMPORTANTE: importar os models para que as tabelas entrem em Base.metadata
# Ajuste os caminhos/nomes conforme estiverem no seu projeto
from app.models.compartment import Compartment  # noqa: F401
from app.models.instance import Instance        # noqa: F401
from app.models.instance_config import InstanceConfig  # noqa: F401
