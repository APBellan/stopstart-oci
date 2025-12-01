from .base_class import Base  # noqa: F401

# Importa todos os models para que o Alembic/SQLAlchemy conheçam as tabelas
from app.models.compartment import Compartment  # noqa: F401
from app.models.instance import Instance  # noqa: F401
from app.models.instance_config import InstanceConfig  # noqa: F401

# Se tiver outros models, importa aqui também
# from app.models.user import User  # noqa: F401
# ...
