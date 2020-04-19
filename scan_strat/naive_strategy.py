from scan_strat.base_strategy import BaseStrategy

from ocr_state.field_state import FieldState
from ocr_state.piece_stats import PieceStatAccumulator
from FullStateOptimizer.FullStateConfiguration import FS_CONFIG
from scan_strat.scan_helpers import (
    scan_full,
    scan_level,
    scan_score,
    scan_lines,
    scan_field,
    scan_preview,
    scan_spawn,
)
from FullStateOptimizer.Transition import TRANSITION

import time


class NaiveStrategy(BaseStrategy):

    # simply tries to get into game
    def update_menu(self):
        pass

    def update_ingame(self):
        pass
