import argparse

args = None


def init_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument(
        "--calibrate", help="Run calibrator rather than scanner", action="store_true"
    )
    parser.add_argument("--defaultconfig", default=None)
    args, unknown = parser.parse_known_args()


if args is None:
    init_args()
