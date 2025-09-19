from typing import TYPE_CHECKING
from peakrdl.plugins.importer import ImporterPlugin #pylint: disable=import-error
from peakrdl.plugins.exporter import ExporterSubcommandPlugin
import re

from .importer import SVDImporter
from .exporter import SVDExporter

if TYPE_CHECKING:
    import argparse
    from systemrdl import RDLCompiler
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

class Importer(ImporterPlugin):
    file_extensions = ["svd"]

    def is_compatible(self, path: str) -> bool:
        # Could be any XML file.
        # See if file contains an ipxact or spirit component tag
        with open(path, "r", encoding="utf-8") as f:
            if re.search(r"CMSIS-SVD", f.read()):
                return True
        return False

    # def add_importer_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
    #     arg_group.add_argument(
    #         "--remap-state",
    #         metavar="STATE",
    #         default=None,
    #         help="Optional remapState string that is used to select memoryRemap regions that are tagged under a specific remap state."
    #     )

    def do_import(self, rdlc: 'RDLCompiler', options: 'argparse.Namespace', path: str) -> None:
        i = SVDImporter(rdlc)
        i.import_file(
            path,
        )
