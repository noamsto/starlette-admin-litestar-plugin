import datetime
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar

from starlette.datastructures import FormData
from starlette.requests import Request
from starlette_admin import RequestAction
from starlette_admin.contrib.sqla.converters import ModelConverter
from starlette_admin.contrib.sqla.view import ModelView
from starlette_admin.converters import converts
from starlette_admin.fields import DateTimeField, StringField
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
            if dt.tzinfo is None:
                # Assume UTC
                dt = dt.replace(tzinfo=datetime.UTC)
            else:
                # Convert to UTC
                dt = dt.astimezone(datetime.UTC)
            return dt
        except (TypeError, ValueError):
            return None

    async def serialize_value(self, request: Request, value: Any, _action: RequestAction) -> str:
        if not isinstance(value, datetime.datetime):
            raise ValueError(f"Expected datetime, got {type(value)}")

        # Ensure value has timezone info
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)

        return format_datetime(value, format="%B %d, %Y %H:%M:%S %Z", tzinfo=datetime.UTC)


class GUIDCoverter(ModelConverter):
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
    exclude_audit_columns_create_edit: ClassVar[bool] = True
    exclude_fields_create_edit_default: Sequence[str] = ["created_at", "updated_at"]

    def __init__(
        self,
        model: type[Any],
        icon: str | None = None,
        name: str | None = None,
        label: str | None = None,
        identity: str | None = None,
    ):
        if self.exclude_sentinel_column:
            self.exclude_fields_from_create.append("_sentinel")  # type: ignore[attr-defined]
            self.exclude_fields_from_edit.append("_sentinel")  # type: ignore[attr-defined]
            self.exclude_fields_from_list.append("_sentinel")  # type: ignore[attr-defined]
            self.exclude_fields_from_detail.append("_sentinel")  # type: ignore[attr-defined]

        if self.exclude_audit_columns_create_edit:
            self.exclude_fields_from_create.extend(  # type: ignore[attr-defined]
                ["created_at", "updated_at"]
            )
            self.exclude_fields_from_edit.extend(  # type: ignore[attr-defined]
                ["created_at", "updated_at"]
            )

        super().__init__(model, icon, name, label, identity, GUIDCoverter())
