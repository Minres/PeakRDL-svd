import os
from peakrdl_ipxact.exporter import Standard
from .unittest_utils import SVDTestCase
from systemrdl.node import RegNode, FieldNode, MemNode


class TestImportExport(SVDTestCase):

    def symmetry_check(self, sources):
        a = self.compile(sources)

        xml_path = "%s.xml" % self.request.node.name

        with self.subTest("export"):
            self.export(a, xml_path)

        with self.subTest("validate xsd"):
            self.validate_xsd(xml_path, self.get_schema_path())

    def test_generic_example(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [os.path.join(this_dir, "test_sources/accellera-generic_example.rdl")]
        )

    def test_nested(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.symmetry_check(
            [
                os.path.join(this_dir, "test_sources/accellera-generic_example.rdl"),
                os.path.join(this_dir, "test_sources/nested.rdl"),
            ]
        )
