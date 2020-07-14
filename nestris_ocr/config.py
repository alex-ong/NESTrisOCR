from nestris_ocr.utils.program_args import args
from nestris_ocr.config_class import Config

config = Config(args.config, auto_save=True, default_config=args.defaultconfig)
