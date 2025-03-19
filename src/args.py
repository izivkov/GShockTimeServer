import argparse
import sys


class Args:
    def __init__(self):
        self.parse_and_store(sys.argv[1:])

    def parse_and_store(self, args):
        parser = argparse.ArgumentParser(description="Parser")
        parser.add_argument(
            "--multi-watch",
            action='store_true',
            help="--multi-watch allows use of multimple watches")
        parser.add_argument(
            "--mailto", help="email when time set to email address", required=False
        )
        parser.add_argument(
            "-l", "--log_level", default="INFO", help="Sets log level", required=False
        )
        self.args = parser.parse_args(args)

    def get(self):
        return self.args


args = Args()
