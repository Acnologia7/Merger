from datetime import datetime
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import Field, RootModel, BaseModel


# -----------------------
# PYDANTIC MODELS
# -----------------------

MenuId = Annotated[int, Field(gt=0)]
Price = Annotated[float, Field(gt=0)]
RatePct = Annotated[float, Field(gt=0)]


class MenuNameMap(RootModel[Dict[str, str]]):
    pass


class MenuItem(BaseModel):
    id: MenuId
    sysName: str
    name: MenuNameMap
    price: Price
    vatRate: Literal["normal", "reduced", "none"]


class VatRate(BaseModel):
    ratePct: RatePct
    isDefault: Optional[bool] = False


class VatRates(RootModel[Dict[str, VatRate]]):
    pass


class DataA(BaseModel):
    menus: List[MenuItem]
    vatRates: VatRates


class DataCResponse(BaseModel):
    data: Dict[str, List[MenuItem]]
    vatRates: Optional[Dict[str, VatRate]] = None
    lastUpdate: datetime
    products: Optional[List[Dict[str, str]]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
