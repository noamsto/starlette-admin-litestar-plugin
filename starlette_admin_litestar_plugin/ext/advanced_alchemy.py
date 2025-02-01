import datetime
from dataclasses import dataclass
from typing import Any

from advanced_alchemy.types import DateTimeUTC
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
    """
    This field is used to represent a value that stores a python datetime.datetime object in UTC.
    All input values are converted to UTC before storage, and displayed in the user's timezone.

    Parameters:
        search_format: moment.js format to send for searching. Use None for iso Format
        output_format: display output format
        assume_local: If True, assumes input without timezone is in local time
    """

    assume_local: bool = True
    class_: str = "field-datetime-utc form-control"

    async def parse_form_data(
        self, request: Request, form_data: FormData, _action: RequestAction
    ) -> datetime.datetime | None:
        try:
            dt = datetime.fromisoformat(form_data.get(self.id))  # type: ignore
            if dt.tzinfo is None:
                if self.assume_local:  # noqa: SIM108
                    # Assume local time and convert to UTC
                    dt = dt.astimezone()
                else:
                    # Assume UTC
                    dt = dt.replace(tzinfo=datetime.UTC)
            else:
                # Convert to UTC
                dt = dt.astimezone(datetime.UTC)
            return dt
        except (TypeError, ValueError):
            return None

    async def serialize_value(self, request: Request, value: Any, action: RequestAction) -> str:
        assert isinstance(value, datetime.datetime), f"Expected datetime, got {type(value)}"

        # Ensure value has timezone info
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)

        if action == RequestAction.EDIT:
            # For edit form, return ISO format in UTC
            return value.astimezone(datetime.UTC).isoformat()
        else:
            # For display, convert to local time
            local_dt = value.astimezone()
            return format_datetime(local_dt, self.output_format)


class GUIDCoverter(ModelConverter):
    @converts("GUID")
    def convert_GUID(self, *args, **kwargs) -> StringField:
        return StringField(
            **self._field_common(*args, **kwargs), **self._string_common(*args, **kwargs)
        )

    @converts(DateTimeUTC)
    def conv_standard_datetime(self, *args: Any, **kwargs: Any) -> DateTimeUTCField:
        return DateTimeUTCField(**self._field_common(*args, **kwargs))


class UUIDModelView(ModelView):
    def __init__(
        self,
        model: type[Any],
        icon: str | None = None,
        name: str | None = None,
        label: str | None = None,
        identity: str | None = None,
    ):
        if self.exclude_fields_from_create:
            self.exclude_fields_from_create.append("_sentinel")  # type: ignore[attr-defined]
        else:
            self.exclude_fields_from_create = ["_sentinel"]

        if self.exclude_fields_from_edit:
            self.exclude_fields_from_edit.append("_sentinel")  # type: ignore[attr-defined]
        else:
            self.exclude_fields_from_edit = ["_sentinel"]

        if self.exclude_fields_from_list:
            self.exclude_fields_from_list.append("_sentinel")  # type: ignore[attr-defined]
        else:
            self.exclude_fields_from_list = ["_sentinel"]

        if self.exclude_fields_from_detail:
            self.exclude_fields_from_detail.append("_sentinel")  # type: ignore[attr-defined]
        else:
            self.exclude_fields_from_detail = ["_sentinel"]

        super().__init__(model, icon, name, label, identity, GUIDCoverter())
