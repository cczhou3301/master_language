"""
Generate Pydantic DTO classes from IDL (app.idl.*_pb2 modules).
Run from backend: python scripts/gen_dto_from_idl.py
Output: app/dto/{auth,user,video}_dto.py and app/dto/__init__.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Map proto module name -> (pb2 module attr name, dto file name)
IDL_MODULES = [
    ("auth", "auth_pb2", "auth_dto"),
    ("user", "user_pb2", "user_dto"),
    ("video", "video_pb2", "video_dto"),
]


def _proto_type_to_python(fd) -> str:
    """Map FieldDescriptor type/label to Python type annotation string."""
    from google.protobuf.descriptor import FieldDescriptor

    t = fd.type
    if fd.label == FieldDescriptor.LABEL_REPEATED:
        if t == FieldDescriptor.TYPE_MESSAGE:
            msg_name = fd.message_type.name
            return f"list[{msg_name}]"
        inner = _scalar_to_python(t)
        return f"list[{inner}]"
    optional = fd.label == FieldDescriptor.LABEL_OPTIONAL
    if t == FieldDescriptor.TYPE_MESSAGE:
        name = fd.message_type.name
        return f"{name} | None" if optional else name
    scalar = _scalar_to_python(t)
    return f"{scalar} | None" if optional else scalar


def _scalar_to_python(t) -> str:
    from google.protobuf.descriptor import FieldDescriptor

    if t in (FieldDescriptor.TYPE_STRING, FieldDescriptor.TYPE_BYTES):
        return "str" if t == FieldDescriptor.TYPE_STRING else "bytes"
    if t in (
        FieldDescriptor.TYPE_INT32,
        FieldDescriptor.TYPE_INT64,
        FieldDescriptor.TYPE_UINT32,
        FieldDescriptor.TYPE_UINT64,
        FieldDescriptor.TYPE_SINT32,
        FieldDescriptor.TYPE_SINT64,
        FieldDescriptor.TYPE_FIXED32,
        FieldDescriptor.TYPE_FIXED64,
        FieldDescriptor.TYPE_SFIXED32,
        FieldDescriptor.TYPE_SFIXED64,
    ):
        return "int"
    if t in (FieldDescriptor.TYPE_FLOAT, FieldDescriptor.TYPE_DOUBLE):
        return "float"
    if t == FieldDescriptor.TYPE_BOOL:
        return "bool"
    return "Any"


def _default_expr(fd) -> str:
    """Default value for Pydantic field."""
    from google.protobuf.descriptor import FieldDescriptor

    if fd.label == FieldDescriptor.LABEL_REPEATED:
        return "Field(default_factory=list)"
    if fd.label == FieldDescriptor.LABEL_OPTIONAL:
        return "= None"
    t = fd.type
    if t == FieldDescriptor.TYPE_STRING or t == FieldDescriptor.TYPE_BYTES:
        return '= ""'
    if t == FieldDescriptor.TYPE_BOOL:
        return "= False"
    if t in (
        FieldDescriptor.TYPE_INT32,
        FieldDescriptor.TYPE_INT64,
        FieldDescriptor.TYPE_UINT32,
        FieldDescriptor.TYPE_UINT64,
    ):
        return "= 0"
    if t in (FieldDescriptor.TYPE_FLOAT, FieldDescriptor.TYPE_DOUBLE):
        return "= 0.0"
    if t == FieldDescriptor.TYPE_MESSAGE:
        return "= None"
    return "= None"


def _get_message_classes(pb2_module):
    """Yield (name, message_class) for each message in the pb2 module."""
    from google.protobuf.message import Message

    for name in dir(pb2_module):
        if name.startswith("_"):
            continue
        obj = getattr(pb2_module, name)
        if isinstance(obj, type) and issubclass(obj, Message):
            yield name, obj


def _order_messages(name_to_cls):
    """Order message names so dependencies come first (same-module refs)."""
    from google.protobuf.descriptor import FieldDescriptor

    order = []
    seen = set()

    def add(name):
        if name in seen:
            return
        seen.add(name)
        cls = name_to_cls.get(name)
        if cls and hasattr(cls, "DESCRIPTOR"):
            for fd in cls.DESCRIPTOR.fields:
                if fd.type == FieldDescriptor.TYPE_MESSAGE and fd.message_type.name in name_to_cls:
                    add(fd.message_type.name)
        order.append(name)

    for n in name_to_cls:
        add(n)
    return order


def generate_dto_file(pb2_module, dto_module_name: str, out_path: Path) -> list[str]:
    """Generate one dto/*_dto.py file; return list of class names."""
    from google.protobuf.descriptor import FieldDescriptor

    name_to_cls = dict(_get_message_classes(pb2_module))
    if not name_to_cls:
        return []

    ordered = _order_messages(name_to_cls)
    lines = [
        f'"""DTOs generated from IDL ({dto_module_name}). Do not edit by hand. Regenerate: python scripts/gen_dto_from_idl.py"""',
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "from pydantic import BaseModel, Field",
        "",
    ]
    class_names = []

    for msg_name in ordered:
        cls = name_to_cls[msg_name]
        class_names.append(msg_name)
        lines.append(f"class {msg_name}(BaseModel):")
        lines.append('    """Generated from idl message."""')
        for fd in cls.DESCRIPTOR.fields:
            py_type = _proto_type_to_python(fd)
            default = _default_expr(fd)
            if default.startswith("Field("):
                lines.append(f"    {fd.name}: {py_type} {default}")
            else:
                lines.append(f"    {fd.name}: {py_type} {default}")
        lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return class_names


def main() -> int:
    out_dir = BACKEND / "app" / "dto"
    out_dir.mkdir(parents=True, exist_ok=True)

    idl = __import__("app.idl", fromlist=["auth_pb2", "user_pb2", "video_pb2"])
    per_module: list[tuple[str, list[str]]] = []

    for _key, pb2_attr, dto_name in IDL_MODULES:
        pb2_module = getattr(idl, pb2_attr, None)
        if pb2_module is None:
            print(f"Skip {pb2_attr}: not found", file=sys.stderr)
            continue
        out_path = out_dir / f"{dto_name}.py"
        class_names = generate_dto_file(pb2_module, pb2_attr, out_path)
        per_module.append((dto_name, class_names))
        print(f"Written {out_path.name}: {class_names}")

    # __init__.py
    init_lines = [
        '"""DTOs generated from IDL. Do not edit by hand. Regenerate: python scripts/gen_dto_from_idl.py"""',
        "from __future__ import annotations",
        "",
    ]
    all_exports = []
    for dto_name, class_names in per_module:
        if class_names:
            init_lines.append(f"from .{dto_name} import {', '.join(class_names)}")
            all_exports.extend(class_names)
    init_lines.append("")
    init_lines.append("__all__ = [")
    for e in all_exports:
        init_lines.append(f'    "{e}",')
    init_lines.append("]")
    init_path = out_dir / "__init__.py"
    init_path.write_text("\n".join(init_lines) + "\n", encoding="utf-8")
    print(f"Updated {init_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
