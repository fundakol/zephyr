import argparse
import subprocess

from west.commands import WestCommand


class UvSync(WestCommand):
    def __init__(self):
        super().__init__(
            'uv_sync', 'run uv sync', "Update the project's environment", accepts_unknown_args=True
        )

    def do_add_parser(self, parser_adder):
        parser = parser_adder.add_parser(
            self.name,
            help=self.help,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=self.description,
            allow_abbrev=False,
        )

        return parser

    def do_run(self, my_args, runner_args):
        subprocess.run(["uv", "sync"])
