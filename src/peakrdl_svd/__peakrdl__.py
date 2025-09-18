from typing import TYPE_CHECKING
import re

from peakrdl.plugins.exporter import ExporterSubcommandPlugin

from .exporter import SVDExporter

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode


class Exporter(ExporterSubcommandPlugin):
    short_desc = "Export the register model to SVD"

    def add_exporter_arguments(self, arg_group: "argparse._ActionsContainer") -> None:
        arg_group.add_argument(
            "--name",
            default=None,
            help="component name. Defaults to top exported component's name",
        )
        arg_group.add_argument("--version", default="1.0", help="version string. [1.0]")
        arg_group.add_argument("--vendor", default="UNSPECIFIED", help="vendor string")

    def do_export(self, top_node: "AddrmapNode", options: "argparse.Namespace") -> None:
        SVDExporter().export(top_node, options.output, component_name=options.name)
