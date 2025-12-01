from typing import List, Optional
from pydantic import BaseModel


class CompartmentBase(BaseModel):
    id: int  # ou UUID, ajuste conforme seu modelo
    ocid: str
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class CompartmentBreadcrumb(BaseModel):
    ocid: str
    name: str

    class Config:
        orm_mode = True


class InstanceWithConfig(BaseModel):
    id: int  # ou UUID
    ocid: str
    display_name: str
    lifecycle_state: str
    region: Optional[str] = None
    availability_domain: Optional[str] = None

    managed: bool
    protection_flag: bool

    class Config:
        orm_mode = True


class CompartmentNavigationResponse(BaseModel):
    tenancy_id: int  # ou str, conforme Tenancy.id
    current: CompartmentBase
    breadcrumbs: List[CompartmentBreadcrumb]
    parent: Optional[CompartmentBase]
    children: List[CompartmentBase]
    instances: List[InstanceWithConfig]
