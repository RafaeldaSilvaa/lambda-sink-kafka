from dataclasses import dataclass


@dataclass
class Credentials:
    host: str
    username: str
    password: str
    database: str
    port: int = None