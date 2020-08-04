from nestris_ocr.scan_strat.scan_helpers import PATTERNS
from nestris_ocr.scan_strat.naive_strategy import NaiveStrategy
from nestris_ocr.ocr_algo.score_fixer import ScoreFixer
from nestris_ocr.scan_strat.scan_helpers import scan_score

# Ideally we run this with the following options:
# Support Hex Level
# Support Hex Scores


class N99Strategy(NaiveStrategy):
    def __init__(self, *args):
        super(N99Strategy, self).__init__(*args)
        self.score_cleaner = ScoreFixer(PATTERNS["score"])

    def scan_score(self, img):
        score = scan_score(img, "OOOOOO")
        self.score = self.score_cleaner.fix(score)
