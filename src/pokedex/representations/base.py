from abc import ABC, abstractmethod


class RepresentationStrategy(ABC):
    name: str

    @abstractmethod
    def render(self, pokemon: dict) -> str: ...
