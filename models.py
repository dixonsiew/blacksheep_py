from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config, Exclude
from pydantic import Field
from typing import Annotated


@dataclass
class Item:
    id: int
    name: str
    description: str
    price: float

@dataclass
class Role:
    id: int = None
    name: str | None = None

@dataclass_json
@dataclass
class User:
    password: str | None = field(metadata=config(exclude=Exclude.ALWAYS))
    id: int = None
    username: str = ""
    first_name: str = ""
    last_name: str | None = None
    last_login: str | None = None
    roles: list[Role] = field(default_factory=list)
    
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