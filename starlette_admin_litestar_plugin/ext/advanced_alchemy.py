import datetime
from dataclasses import dataclass
from typing import Any, ClassVar

from pydantic import BaseModel, ValidationError
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette_admin import RequestAction
from starlette_admin.contrib.sqla.converters import ModelConverter
from starlette_admin.contrib.sqla.view import ModelView
from starlette_admin.converters import converts
from starlette_admin.fields import DateTimeField, StringField
from starlette_admin.helpers import pydantic_error_to_form_validation_errors
from starlette_admin.i18n import format_datetime


@dataclass
class DateTimeUTCField(DateTimeField):
    """Custom field for handling datetime values in UTC timezone."""

    form_alt_format: str | None = "F j, Y  H:i:S (\\UTC)"

    async def parse_form_data(
        self, request: Request, form_data: FormData, _action: RequestAction
    ) -> datetime.datetime | None:
        try:
            dt = datetime.datetime.fromisoformat(form_data.get(self.id))  # type: ignore
            dt.astimezone()
            return dt
        except (TypeError, ValueError):
            return None

    async def serialize_value(self, request: Request, value: Any, _action: RequestAction) -> str:
        if not isinstance(value, datetime.datetime):
            raise ValueError(f"Expected datetime, got {type(value)}")

        # Make sure datetime have timezone info
        value = value.astimezone()
        return format_datetime(value, format="%B %d, %Y %H:%M:%S %Z")


class AdvancedAlchemyCoverter(ModelConverter):
    @converts("GUID")
    def convert_GUID(self, *args, **kwargs) -> StringField:
        return StringField(
            **self._field_common(*args, **kwargs), **self._string_common(*args, **kwargs)
        )

    @converts("DateTimeUTC")
    def conv_standard_datetime(self, *args: Any, **kwargs: Any) -> DateTimeUTCField:
        return DateTimeUTCField(**self._field_common(*args, **kwargs))


class UUIDModelView(ModelView):
    exclude_sentinel_column: ClassVar[bool] = True
    read_only_audit_columns: ClassVar[bool] = True

    def __init__(
        self,
        model: type[Any],
        icon: str | None = None,
        name: str | None = None,
        label: str | None = None,
        identity: str | None = None,
        pydantic_model: type[BaseModel] | None = None,
    ):
        self.pydantic_model = pydantic_model
        if self.exclude_sentinel_column:
            self.exclude_fields_from_create.append("_sentinel")  # type: ignore[attr-defined]
            self.exclude_fields_from_edit.append("_sentinel")  # type: ignore[attr-defined]
            self.exclude_fields_from_list.append("_sentinel")  # type: ignore[attr-defined]
            self.exclude_fields_from_detail.append("_sentinel")  # type: ignore[attr-defined]

        if self.read_only_audit_columns:
            self.exclude_fields_from_create.extend(  # type: ignore[attr-defined]
                ["created_at", "updated_at"]
            )
            self.exclude_fields_from_edit.extend(  # type: ignore[attr-defined]
                ["created_at", "updated_at"]
            )

        super().__init__(model, icon, name, label, identity, AdvancedAlchemyCoverter())

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        if not self.pydantic_model:
            return

        try:
            self.pydantic_model(**data)
        except ValidationError as error:
            raise pydantic_error_to_form_validation_errors(error) from error
