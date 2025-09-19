from typing import Union, Optional, TYPE_CHECKING, Any
import enum

from xml.dom import minidom
import xml.etree.ElementTree as ET
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


# ===============================================================================
class SVDExporter:
    msg: "MessageHandler"

    # ---------------------------------------------------------------------------
    def __init__(self, **kwargs: Any) -> None:
        """
        Constructor for the exporter object.

        Parameters
        ----------
        #out_path: str
        #    name of the output file
        """

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
        self.msg = node.env.msg
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
        device.add_address_config(width=32, unit_bits=8)
        self._extract_peripherals(node, device)
        # Create a svd file and format it nicely (copied from device.dump(path))
        svd = ET.ElementTree(device.root)
        svd.write(
            path,
            encoding="UTF-8",
            xml_declaration=True,
        )
        with open(path, "r") as f:
            formated = minidom.parseString(f.read()).toprettyxml(indent="  ")

        with open(path, "w") as f:
            f.write(formated)

    # ---------------------------------------------------------------------------
    def _extract_peripherals(self, node, device: SvdDevice):
        for child in node.children():
            if any(isinstance(ele, RegNode) for ele in child.children()):
                peripheral: SvdPeripheral = device.add_peripheral(
                    child.get_property("name"), version=str(self.version)
                )  # type: ignore
                desc = child.get_property("desc")
                if desc:
                    peripheral.add_description(desc)
                peripheral.add_base_address(child.absolute_address)
                # peripheral.add_size(child.get_property("width"))
                self._extract_registers(child, peripheral, 0)
            elif isinstance(child, AddrmapNode) or isinstance(child, RegfileNode):
                self._extract_peripherals(child, device)
            elif not isinstance(child, MemNode):
                self.msg.warning(f"Don't know what to do with {child}")

    # ---------------------------------------------------------------------------
    def _extract_registers(self, node, peripheral: SvdPeripheral, addr_offset):
        for child in node.children():
            if isinstance(child, RegNode):
                # Add a register to the peripheral.
                reg: SvdRegister = peripheral.add_register(child.get_property("name"))  # type: ignore
                desc = child.get_property("desc")
                if desc:
                    reg.add_description(desc)
                reg.add_offset_address(child.address_offset)
                reg.add_size(child.get_property("regwidth"))
                reset_bits = self._extract_fields(child, reg)
                reset_val = 0
                for k, v in reset_bits.items():
                    reset_val = reset_val | v << k
                reg.add_reset_value(reset_val)
            elif isinstance(child, AddrmapNode) or isinstance(child, RegfileNode):
                self._extract_registers(
                    child, peripheral, addr_offset + child.address_offset
                )
            else:
                self.msg.error(f"We should not arrive here!")

    # ---------------------------------------------------------------------------
    def _extract_fields(self, node, register: SvdRegister):
        reset_values = {}
        for field in node.fields():
            if isinstance(field, FieldNode):
                # Add fields to the register.
                reg_field: SvdRegisterField = register.add_field(
                    field.get_property("name")
                )  # type: ignore
                desc = field.get_property("desc")
                if desc:
                    reg_field.add_description(desc)
                reg_field.add_bit_range(first_bit=field.low, last_bit=field.high)
                reg_field.add_access_permission(
                    read=field.is_sw_readable, write=field.is_sw_writable
                )
                reset_val = field.get_property("reset")
                if isinstance(reset_val, int):
                    # collect reset values bit by bit
                    for i in range(field.low, field.high + 1):
                        reset_values[i] = reset_val >> (i - field.low) & 0x1
        return reset_values
