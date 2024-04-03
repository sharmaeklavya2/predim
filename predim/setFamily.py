from __future__ import annotations
import json
from collections.abc import Sequence, Mapping
import itertools
import warnings
from typing import Optional
from .common import IdInfo, JsonVal
from .common import assertType, assertOptionalType, assertSeqOfPairs


def getInputTypeErrorMsg(purpose: str, t: type) -> str:
    return f'invalid input type for {purpose}: {t.__name__}'


class SetFamily:
    def __init__(self, info: IdInfo):
        self.info = info

    @staticmethod
    def fromJson(obj: JsonVal) -> SetFamily:
        assert isinstance(obj, Mapping)
        typeName = assertType(obj['type'], str)
        if typeName == 'dag':
            return DagSetFamily.fromJson(obj)
        elif typeName == 'bool':
            return BoolSetFamily.fromJson(obj)
        elif typeName == 'prod':
            return ProdSetFamily.fromJson(obj)
        else:
            raise TypeError(f'unrecognized type {typeName}')

    def __repr__(self) -> str:
        return '{}({})'.format(type(self).__name__, repr(self.info.name))

    def validateInput(self, x: object) -> object:
        raise NotImplementedError()

    def intersect(self, a: object, b: object) -> Sequence[object]:
        raise NotImplementedError()

    def contains(self, a: object, b: object) -> bool:
        raise NotImplementedError()


class DagSetFamily(SetFamily):
    def __init__(self, info: IdInfo, default: Optional[str], values: Sequence[IdInfo],
            containments: Sequence[tuple[str, str]]):
        super().__init__(info)
        self.values = values
        self.default = default
        self.nameToValue = {x.name: x for x in values}
        assert len(self.values) == len(self.nameToValue)
        self.containments = set(containments)

    @staticmethod
    def fromJson(obj: JsonVal) -> DagSetFamily:
        assert isinstance(obj, Mapping)
        info = IdInfo.fromJson(obj)
        valuesObj = obj['values']
        default = assertOptionalType(obj.get('default'), str)
        assert not isinstance(valuesObj, str) and isinstance(valuesObj, Sequence)
        values = [IdInfo.fromJson(sObj) for sObj in valuesObj]
        containments = assertSeqOfPairs(obj['containments'], str)
        return DagSetFamily(info, default, values, containments)

    def validateInput(self, x: object) -> str:
        if x is None and self.default is not None:
            return self.default
        elif isinstance(x, str):
            if x in self.nameToValue.keys():
                return x
            else:
                raise ValueError(f'invalid input value for {type(self).__name__}: {x}')
        else:
            raise TypeError(getInputTypeErrorMsg(type(self).__name__, type(x)))

    def intersect(self, aOrig: object, bOrig: object) -> Sequence[str]:
        warnings.warn('DagSetFamily.intersect is incorrect')
        a, b = self.validateInput(aOrig), self.validateInput(bOrig)
        if (a, b) in self.containments:
            return (b,)
        elif (b, a) in self.containments:
            return (a,)
        else:
            return ()

    def contains(self, aOrig: object, bOrig: object) -> bool:
        warnings.warn('DagSetFamily.contains is incorrect')
        a, b = self.validateInput(aOrig), self.validateInput(bOrig)
        return (a, b) in self.containments


class BoolSetFamily(SetFamily):
    def __init__(self, info: IdInfo):
        super().__init__(info)

    @staticmethod
    def fromJson(obj: JsonVal) -> BoolSetFamily:
        info = IdInfo.fromJson(obj)
        return BoolSetFamily(info)

    def validateInput(self, x: object) -> bool:
        if x is None or x is False:
            return False
        elif x is True:
            return True
        else:
            raise TypeError(getInputTypeErrorMsg(type(self).__name__, type(x)))

    def intersect(self, aOrig: object, bOrig: object) -> Sequence[bool]:
        a, b = self.validateInput(aOrig), self.validateInput(bOrig)
        return (a or b,)

    def contains(self, aOrig: object, bOrig: object) -> bool:
        a, b = self.validateInput(aOrig), self.validateInput(bOrig)
        return (not a) or b


class ProdSetFamily(SetFamily):
    def __init__(self, info: IdInfo, parts: Sequence[SetFamily]):
        super().__init__(info)
        self.parts = parts

    def __repr__(self) -> str:
        return '{}({}, parts={})'.format(type(self).__name__, self.info.name,
            [part.info.name for part in self.parts])

    @staticmethod
    def fromJson(obj: JsonVal) -> ProdSetFamily:
        assert isinstance(obj, Mapping)
        info = IdInfo.fromJson(obj)
        partsObj = obj['parts']
        assert isinstance(partsObj, Sequence)
        parts = [SetFamily.fromJson(partObj) for partObj in partsObj]
        return ProdSetFamily(info, parts)

    def validateInput(self, x: object) -> tuple[object, ...]:
        if isinstance(x, Mapping):
            return tuple([x.get(part.info.name) for part in self.parts])
        elif isinstance(x, Sequence):
            if len(x) != len(self.parts):
                raise ValueError('input to ProdSetFamily({}) has length {} instead of {}'.format(
                    self.info.name, len(x), len(self.parts)))
            else:
                return tuple(x)
        else:
            raise TypeError(getInputTypeErrorMsg(type(self).__name__, type(x)))

    def intersect(self, aOrig: object, bOrig: object) -> Sequence[tuple[object, ...]]:
        a, b = self.validateInput(aOrig), self.validateInput(bOrig)
        answers = []
        for i, part in enumerate(self.parts):
            answers.append(part.intersect(a[i], b[i]))
        return list(itertools.product(*answers))

    def contains(self, aOrig: object, bOrig: object) -> bool:
        a, b = self.validateInput(aOrig), self.validateInput(bOrig)
        for i, part in enumerate(self.parts):
            if not part.contains(a[i], b[i]):
                return False
        return True


def loadSetFamilyFromFile(fpath: str) -> SetFamily:
    with open(fpath) as fp:
        obj = json.load(fp)
    return SetFamily.fromJson(obj)
