from __future__ import annotations
import json
from collections.abc import Sequence, Mapping
from .common import IdInfo, JsonVal, assertType, assertSeqOfPairs


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


class DagSetFamily(SetFamily):
    def __init__(self, info: IdInfo, values: Sequence[IdInfo], containments: Sequence[tuple[str, str]]):
        super().__init__(info)
        self.values = values
        self.containments = containments

    @staticmethod
    def fromJson(obj: JsonVal) -> DagSetFamily:
        assert isinstance(obj, Mapping)
        info = IdInfo.fromJson(obj)
        valuesObj = obj['values']
        assert not isinstance(valuesObj, str) and isinstance(valuesObj, Sequence)
        values = [IdInfo.fromJson(sObj) for sObj in valuesObj]
        containments = assertSeqOfPairs(obj['containments'], str)
        return DagSetFamily(info, values, containments)


class BoolSetFamily(SetFamily):
    def __init__(self, info: IdInfo):
        super().__init__(info)

    @staticmethod
    def fromJson(obj: JsonVal) -> BoolSetFamily:
        info = IdInfo.fromJson(obj)
        return BoolSetFamily(info)


class ProdSetFamily(SetFamily):
    def __init__(self, info: IdInfo, parts: Sequence[SetFamily]):
        super().__init__(info)
        self.parts = parts

    @staticmethod
    def fromJson(obj: JsonVal) -> ProdSetFamily:
        assert isinstance(obj, Mapping)
        info = IdInfo.fromJson(obj)
        partsObj = obj['parts']
        assert isinstance(partsObj, Sequence)
        parts = [SetFamily.fromJson(partObj) for partObj in partsObj]
        return ProdSetFamily(info, parts)


def loadSetFamilyFromFile(fpath: str) -> SetFamily:
    with open(fpath) as fp:
        obj = json.load(fp)
    return SetFamily.fromJson(obj)
