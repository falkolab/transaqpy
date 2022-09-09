from __future__ import annotations
import sys
from typing import Union, Optional

import lxml.etree as et
encoding = sys.stdout.encoding

TRANSAQ_TIME_FORMAT = "%d.%m.%Y %H:%M:%S"


class CommandMaker:
    _root: et.Element

    def __init__(self, _id: str = None, parent: et.Element = None, tag: str = 'command', **kw):
        if _id:
            self._root = et.Element(tag, id=_id, **kw)
            assert parent is None, "The `parent` argument should not be passed apart with id"
        elif parent is not None and tag is not None:
            self._root = self._make_el(tag, None)
            parent.append(self._root)
        else:
            self._root = et.Element(tag, **kw)

    @property
    def root(self):
        return self._root

    def add(self, tag: Union[dict, str], text: Optional[Union[str, dict]] = None) -> CommandMaker:
        for tag, text in tag.items() if isinstance(tag, dict) else [(tag, text,)]:
            self._root.append(self._make_el(tag, text))
        return self

    def _make_el(self, tag: str, text: Optional[Union[str, dict]]) -> et.Element:
        el = et.Element(tag)
        if text is None:
            pass
        elif isinstance(text, dict):
            for k, v in text.items():
                el.append(self._make_el(k, v))
        else:
            el.text = str(text)
            if isinstance(text, bool):
                el.text = el.text.lower()
        return el

    def encode(self, _encoding="utf-8"):
        return et.tostring(self._root, encoding=_encoding)
