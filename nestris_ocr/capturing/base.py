from abc import ABC, abstractmethod
from PIL import Image


class AbstractCapture(ABC):
    def __init__(self, source_id: str):
        self.source_id = source_id

    @abstractmethod
    def get_image(self) -> (int, Image):
        pass
