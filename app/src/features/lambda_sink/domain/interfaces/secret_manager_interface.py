from abc import ABC, abstractmethod


class ISecretManager(ABC):
    @abstractmethod
    def get_secret(self) -> dict:
        pass