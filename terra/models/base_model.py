#  Copyright 2022 Terra Enabling Developers Limited
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from __future__ import annotations

import dataclasses
import enum
import pydoc
import typing

PRIMITIVES = (str, int, bool, float, type(None), dict)
datamodelT = typing.TypeVar("datamodelT", bound="TerraDataModel")


class ImplementsToDict(typing.Protocol):
    def to_dict(self) -> typing.Dict[str, typing.Any]:
        ...


class TerraDataModel:
    """
    Base class for all data models that terra returns.
    """

    def _get_attrs(self) -> typing.Iterable[str]:
        return filter(
            lambda a: not a.startswith("_"),
            set(dir(self)).difference(set(dir(TerraDataModel))),
        )

    def keys(self) -> typing.Generator[str, None, None]:
        yield from self._get_attrs()

    def values(self) -> typing.Generator[typing.Any, None, None]:
        attrs = self._get_attrs()
        yield from (getattr(self, attr) for attr in attrs)

    def items(self) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
        attrs = self._get_attrs()
        for attr in attrs:
            yield attr, getattr(self, attr)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """
        Get the dictionary (json) representation of the data model.

        This method inspects the attributes of the instance that it is being called on
        to determine how to build the correct payload from the data stored.

        Returns:
            :obj:`dict`: Dictionary representation of the data model.
        """
        attrs = self._get_attrs()

        output: typing.Dict[typing.Any, typing.Any] = {}
        for attr in attrs:
            attr_val = getattr(self, attr)
            if isinstance(attr_val, enum.IntEnum):
                output[attr] = int(attr_val)
            elif type(attr_val) in PRIMITIVES:
                output[attr] = attr_val
            elif isinstance(attr_val, list):
                if (attr_val and type(attr_val[0]) in PRIMITIVES) or not attr_val:
                    output[attr] = attr_val
                else:
                    output[attr] = [item.to_dict() for item in attr_val]
            else:
                output[attr] = attr_val.to_dict()
        return output

    @classmethod
    def from_dict(
        cls: typing.Type[datamodelT], model_dict: typing.Dict[str, typing.Any], safe: bool = False
    ) -> datamodelT:
        """
        Return the Class data model representation of the dictionary (json).

        This method inspects the attributes of the class that it is being called on
        to determine how to build the correct payload from the data stored.

        Args:
            model_dict:obj:`dict`:
            safe:obj:`bool`:

        Returns:
            :obj:`terrpython.models.base_model.TerraDataModel`
        """
        data_model = cls()
        for k, v in model_dict.items():
            if (
                (inner_item := getattr(data_model, k, *(("NOT_FOUND",) if safe else ()))) in [None, []]
                or isinstance(inner_item, TerraDataModel)
                or isinstance(v, list)
            ):

                if isinstance(inner_item, TerraDataModel):
                    v = inner_item.from_dict(v)

                # if it's a list
                if isinstance(v, list):

                    if v != []:

                        # getting all the field types of the current class
                        z = {field.name: field.type for field in dataclasses.fields(cls())}

                        # getting the current field name
                        current_field_name = str(z[k]).split("[")[1].split("]")[0]

                        # adding terra before the name
                        if current_field_name.split(".")[0] == "models":
                            current_field_name = "terra." + current_field_name

                        # checking if the elements of the list are Terra Data Models
                        if current_field_name.split(".")[0] == "terra":

                            result = []

                            # for each dictionnary inside the list
                            for inner_dict in v:

                                # the type of the item inside the list
                                inner_data_model = typing.cast(
                                    typing.Type[TerraDataModel], pydoc.locate(current_field_name)
                                )()
                                # fill up the model
                                inner_data_model = inner_data_model.from_dict(inner_dict)
                                # append the model to the result list
                                result.append(inner_data_model)

                            v = result

                setattr(data_model, k, v)

        return data_model

    @classmethod
    def from_dict_api(
        cls: typing.Type[datamodelT], model_dict: typing.Dict[str, typing.Any], safe: bool = False
    ) -> datamodelT:
        """
        Return the Class data model representation of the dictionary (json).

        This method inspects the attributes of the class that it is being called on
        to determine how to build the correct payload from the data stored.

        Args:
            model_dict:obj:`dict`:
            safe:obj:`bool`:

        Returns:
            :obj:`terrpython.models.base_model.TerraDataModel`
        """
        data_model = cls()
        for k, v in model_dict.items():
            if (inner_item := getattr(data_model, k, *(("NOT_FOUND",) if safe else ()))) in [None, []] or isinstance(
                inner_item, TerraDataModel
            ):
                if isinstance(inner_item, TerraDataModel):

                    v = inner_item.from_dict_api(v)

                setattr(data_model, k, v)

        return data_model

    def populate_from_dict(
        self: datamodelT, model_dict: typing.Dict[str, typing.Any], safe: bool = False
    ) -> datamodelT:
        """
        Populates missing data fields in the class given a dictionary (json).

        This method inspects the attributes of the instance that it is being called on
        to determine how to build the correct payload from the data stored.

        Args:
            model_dict:obj:`dict`:
            safe:obj:`bool`:

        Returns:
            :obj:`terrpython.models.base_model.TerraDataModel`
        """
        for k, v in model_dict.items():
            if getattr(self, k, *(("NOT_FOUND",) if safe else ())) is None:
                setattr(self, k, v)

        return self
