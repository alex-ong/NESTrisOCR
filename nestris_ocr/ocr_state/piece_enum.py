from enum import Enum


class Piece(Enum):
    T = 0
    J = 1
    Z = 2
    O = 3  # noqa: E741
    S = 4
    L = 5
    I = 6  # noqa: E741
    EMPTY = 7
    UNKNOWN = 8
