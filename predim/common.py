from __future__ import annotations
from collections.abc import Sequence, Mapping
from typing import NamedTuple, Optional, TypeVar, Union


T = TypeVar('T')
JsonVal = Union[None, bool, str, float, int, Sequence['JsonVal'], Mapping[str, 'JsonVal']]


def assertType(value: object, t: type[T]) -> T:
    if isinstance(value, t):
        return value
    else:
        raise TypeError(f'expected type {t.__name__}, got {type(value).__name__}')


def assertOptionalType(value: object, t: type[T]) -> Optional[T]:
    if value is None or isinstance(value, t):
        return value
    else:
        raise TypeError(f'expected type Optional[{t.__name__}], got {type(value).__name__}')


def assertSeq(value: object, t: type[T]) -> Sequence[T]:
    if not isinstance(value, Sequence):
        raise TypeError(f'expected a Sequence, got {type(value).__name__}')
    for i, x in enumerate(value):
        if not isinstance(x, t):
            raise TypeError(f'[{i}]: expected type {t.__name__}, got {type(x).__name__}')
    return value


def assertSeqOfPairs(value: object, t: type[T]) -> Sequence[tuple[T, T]]:
    if not isinstance(value, Sequence):
        raise TypeError(f'expected a Sequence, got {type(value).__name__}')
    v2 = []
    for i, x in enumerate(value):
        y1, y2 = assertSeq(x, t)
        v2.append((y1, y2))
    return v2


class IdInfo(NamedTuple):
    name: str
    label: Optional[str] = None
    text: Optional[str] = None
    link: Optional[str] = None

    @staticmethod
    def fromJson(obj: JsonVal) -> IdInfo:
        assert isinstance(obj, Mapping)
        name = assertType(obj['name'], str)
        label = assertType(obj.get('label', name), str)
        text = assertOptionalType(obj.get('text'), str)
        link = assertOptionalType(obj.get('link'), str)
        return IdInfo(name=name, label=label, text=text, link=link)
