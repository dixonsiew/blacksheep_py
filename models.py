from dataclasses import dataclass


@dataclass
class Item:
    id: int
    name: str
    description: str
    price: float

@dataclass
class CommonSetup:
    id: int = None
    code: str = ""
    created_by: int = None
    created_date: str = ""
    deleted: bool = False
    deleted_by: int = None
    deleted_date: str = ""
    desc: str = ""
    modified_by: int = None
    modified_date: str = ""
    ref: str = ""