from typing import Union, Optional, TYPE_CHECKING, Any
import enum

from xml.dom import minidom
from systemrdl.rdltypes import AccessType
from systemrdl.node import (
    Node,
    RootNode,
    AddrmapNode,
    MemNode,
    RegNode,
    RegfileNode,
    FieldNode,
)
from cmsis_svd_codec import SvdDevice
from cmsis_svd_codec.encoder import SvdPeripheral, SvdRegister, SvdRegisterField

if TYPE_CHECKING:
    from systemrdl.messages import MessageHandler

# sw <--> ipxact:access
ACCESS_MAP = {
    # (read=True, write=False)
    AccessType.r: (True, False),
    AccessType.rw: (True, True),
    AccessType.rw1: (True, True),
    AccessType.w: (False, True),
    AccessType.w1: (False, True),
}


# ===============================================================================
class SVDExporter:
    msg: "MessageHandler"

    def __init__(self, **kwargs: Any) -> None:
        """
        Constructor for the exporter object.

        Parameters
        ----------
        #out_path: str
        #    name of the output file
        """

        # self.out_path = kwargs.pop("out_path", None) or "output.svd"
        self.vendor = kwargs.pop("vendor", None) or "UNSPECIFIED"
        self.version = kwargs.pop("version", None) or "1.0"

        # Check for stray kwargs
        if kwargs:
            raise TypeError(
                "got an unexpected keyword argument '%s'" % list(kwargs.keys())[0]
            )

    # ---------------------------------------------------------------------------
    def export(
        self, node: Union[AddrmapNode, RootNode], path: str, **kwargs: Any
    ) -> None:
        """
        Parameters
        ----------
        node: AddrmapNode
            Top-level SystemRDL node to export.
        path:
            Path to save the exported XML file.
        component_name: str
            SVD component name. If unspecified, uses the top node's name upon export.
        """

        component_name = kwargs.pop("component_name", None) or node.inst_name

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            node = node.top

        if not isinstance(node, (AddrmapNode, MemNode)):
            raise TypeError(
                "'node' argument expects type AddrmapNode or MemNode. Got '%s'"
                % type(node).__name__
            )

        if isinstance(node, AddrmapNode) and node.get_property("bridge"):
            self.msg.warning(
                "SVD generator does not have proper support for bridge addmaps yet. The 'bridge' property will be ignored.",
                node.inst.property_src_ref.get("bridge", node.inst.inst_src_ref),
            )

        device = SvdDevice(self.vendor, component_name, version="1.0")
        # Fill the device top level details.
        device.add_description(str(node.get_property("desc")))
        device.add_license(
            """Licensed under the Apache License, Version 2.0, see LICENSE for details."""
        )
        self._extract_peripherals(node, device)

        # Create a svd file.
        device.dump(path)

    def _extract_peripherals(self, node, device: SvdDevice):
        for child in node.children():
            if any(isinstance(ele, RegNode) for ele in child.children()):
                peripheral = device.add_peripheral(
                    child.get_property("name"), version=str(self.version)
                )
                peripheral.add_description(child.get_property("desc"))
                peripheral.add_base_address(child.absolute_address)
                # peripheral.add_size(child.get_property("width"))
                self._extract_registers(child, peripheral)
            elif isinstance(child, AddrmapNode) or isinstance(child, RegfileNode):
                self._extract_peripherals(child, device)
            elif not isinstance(child, MemNode):
                print(f"Don't know what to do with {child}")

    def _extract_registers(self, node, peripheral: SvdPeripheral):
        for child in node.children():
            if isinstance(child, RegNode):
                # Add a register to the peripheral.
                reg = peripheral.add_register(child.get_property("name"))
                reg.add_description(child.get_property("desc"))
                reg.add_offset_address(child.absolute_address)
                self._extract_fields(child, reg)
            elif isinstance(child, AddrmapNode) or isinstance(child, RegfileNode):
                self._extract_registers(child, device)
            else:
                print(f"We should not arrive here!")

    def _extract_fields(self, node, register: SvdRegister):
        for field in node.fields():
            if isinstance(field, FieldNode):
                # Add fields to the register.
                reg_field = register.add_field(field.get_property("name"))
                reg_field.add_description(field.get_property("desc"))
                reg_field.add_bit_range(first_bit=field.low, last_bit=field.high)
                sw = field.get_property("sw")
                acc = ACCESS_MAP[sw]
                reg_field.add_access_permission(read=acc[0], write=acc[1])
