from nestris_ocr.config import config


def get_strategy_class():
    strategy = config["performance.scan_strat"]
    if strategy == "NAIVE":
        from nestris_ocr.scan_strat.naive_strategy import NaiveStrategy

        return NaiveStrategy
    elif strategy == "FASTEST":
        from nestris_ocr.scan_strat.fastest_strategy import FastestStrategy

        return FastestStrategy
    elif strategy == "N99":
        from nestris_ocr.scan_strat.n99_strategy import N99Strategy

        return N99Strategy


Strategy = get_strategy_class()
