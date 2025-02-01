from typing import Any

from starlette_admin.contrib.sqla.converters import ModelConverter
from starlette_admin.contrib.sqla.view import ModelView
from starlette_admin.converters import converts
from starlette_admin.fields import StringField


class GUIDCoverter(ModelConverter):
    @converts("GUID")
    def convert_GUID(self, *args, **kwargs) -> StringField:
        return StringField(
            **self._field_common(*args, **kwargs), **self._string_common(*args, **kwargs)
        )


class UUIDModelView(ModelView):
    def __init__(
        self,
        model: type[Any],
        icon: str | None = None,
        name: str | None = None,
        label: str | None = None,
        identity: str | None = None,
    ):
        super().__init__(model, icon, name, label, identity, GUIDCoverter())
        if self.exclude_fields_from_create:
            self.exclude_fields_from_create.append("sentinel")  # type: ignore[attr-defined]
        else:
            self.exclude_fields_from_create = ["sentinel"]

        if self.exclude_fields_from_edit:
            self.exclude_fields_from_edit.append("sentinel")  # type: ignore[attr-defined]
        else:
            self.exclude_fields_from_edit = ["sentinel"]

        if self.exclude_fields_from_list:
            self.exclude_fields_from_list.append("sentinel")
        else:
            self.exclude_fields_from_list = ["sentinel"]

        if self.exclude_fields_from_detail:
            self.exclude_fields_from_detail.append("sentinel")
        else:
            self.exclude_fields_from_detail = ["sentinel"]
