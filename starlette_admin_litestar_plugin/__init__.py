from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, cast

from litestar import asgi
from litestar.plugins.base import InitPluginProtocol
from litestar.types.empty import Empty
from litestar.utils.empty import value_or_default
from starlette.applications import Starlette
from starlette_admin.contrib.sqla import Admin

if TYPE_CHECKING:
    from collections.abc import Sequence

    from litestar.config.app import AppConfig
    from litestar.types.asgi_types import Receive, Scope, Send
    from litestar.types.empty import EmptyType
    from sqlalchemy.engine import Engine
    from sqlalchemy.ext.asyncio import AsyncEngine
    from sqlalchemy.orm import sessionmaker
    from starlette import types as st_types
    from starlette.middleware import Middleware
    from starlette_admin import CustomView, I18nConfig
    from starlette_admin.auth import AuthProvider, BaseAuthProvider
    from starlette_admin.contrib.sqla import ModelView

__all__ = ("StarletteAdminPlugin",)

logger = logging.getLogger(__name__)


@dataclass
class StarlettAdminPluginConfig:
    """Configuration class for Starlette Admin integration with Litestar.

    Attributes:
        views: List of ModelView instances to register with the admin interface
        engine: SQLAlchemy engine instance (sync or async) for database operations
        title: Custom title for the admin interface
        base_url: Base URL path for the admin interface (default: '/admin')
        route_name: Name for the admin route group
        logo_url: URL to the logo image displayed in the admin header
        login_logo_url: URL to the logo image displayed on the login page
        templates_dir: Custom directory path for overriding default admin templates
        statics_dir: Custom directory path for static files
        index_view: Custom view class for the admin index page
        auth_provider: Authentication provider implementation
        middlewares: List of middleware to apply to admin routes
        debug: Enable debug mode for additional logging and details
        i18n_config: Internationalization configuration
        favicon_url: URL to the favicon for the admin interface

    Example:
        .. code-block:: python
            config = StarlettAdminPluginConfig(
                title="My Admin",
                views=[
                    UserAdmin(),
                    PostAdmin(),
                ],
                engine=engine,
                auth_provider=MyAuthProvider(),
            )
    """

    views: Sequence[ModelView] | EmptyType = Empty
    engine: Engine | AsyncEngine | EmptyType = Empty
    title: str | EmptyType = Empty
    base_url: str | EmptyType = Empty
    route_name: str | EmptyType = Empty
    logo_url: str | EmptyType = Empty
    login_logo_url: str | EmptyType = Empty
    templates_dir: str | EmptyType = Empty
    statics_dir: str | EmptyType = Empty
    index_view: CustomView | EmptyType = Empty
    auth_provider: BaseAuthProvider | EmptyType = Empty
    middlewares: Sequence[Middleware] | EmptyType = Empty
    debug: bool = False
    i18n_config: I18nConfig | EmptyType = Empty
    favicon_url: str | EmptyType = Empty

    def to_dict(self):
        """Convert config to dictionary, excluding unset (Empty) values."""
        result = {}
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if value is not Empty:
                result[field] = value
        return result


class StarletteAdminPlugin(InitPluginProtocol):
    def __init__(
        self,
        *,
        starlette_admin_config: StarlettAdminPluginConfig,
    ) -> None:
        """Initializes the starlette-adminPlugin."""
        self.views = list(value_or_default(starlette_admin_config.views, []))
        self.starlette_app = Starlette()
        config_dict = starlette_admin_config.to_dict()
        config_dict.pop("views")
        self.admin = Admin(**config_dict)
        self.admin.mount_to(self.starlette_app, redirect_slashes=False)
        self.starlette_app.add_middleware(PathFixMiddleware, base_url=self.admin.base_url)
        # disables redirecting based on absence/presence of trailing slashes
        self.starlette_app.router.redirect_slashes = False

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        for view in self.views:
            self.admin.add_view(view)

        mount_path = self.admin.base_url.rstrip("/")

        @asgi(mount_path, is_mount=True)
        async def wrapped_app(scope: Scope, receive: Receive, send: Send) -> None:
            """Wrapper for the starlette-admin app.

            Performs, and unwinds, the necessary scope modifications for the starlette-admin app.
            """
            try:
                await self.starlette_app(_prepare_scope(scope, mount_path), receive, send)  # type: ignore[arg-type]
            except Exception:
                logger.exception("Error raised from starlette-admin app")

        app_config.route_handlers.append(wrapped_app)
        return app_config


class PathFixMiddleware:
    """Middleware for fixing the path in scope for transition b/w Litestar and Starlette.

    See: https://github.com/encode/starlette/issues/869

    If a route is registered with `Mount` on a Starlette app, it needs a trailing slash. However,
    paths registered with `Route` are not found if they have a trailing slash.

    starlette-admin uses `Mount` to register the admin app, and the admin app contains `Route`s.

    Litestar forwards all paths without a leading forward slash, and with a trailing one.

    This middleware fixes the path in the scope to ensure that the path is set correctly for the
    admin app, depending on whether the request forwarded to the admin app is the base url of the
    admin app or not.
    """

    def __init__(self, app: st_types.ASGIApp, *, base_url: str) -> None:
        self.app = app
        self.base_url = base_url.rstrip("/")

    async def __call__(
        self, scope: st_types.Scope, receive: st_types.Receive, send: st_types.Send
    ) -> None:
        orig_path = scope["path"]
        orig_raw = scope["raw_path"]

        path = f"/{scope['path'].lstrip('/').rstrip('/')}"
        if path == self.base_url:
            path = f"{path}/"

        scope["path"] = path
        scope["raw_path"] = scope["path"].encode("utf-8")

        def reset_paths() -> None:
            scope["path"] = orig_path
            scope["raw_path"] = orig_raw

        async def send_wrapper(message: Any) -> None:
            reset_paths()
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            reset_paths()


def _prepare_scope(scope: Scope, mount_path: str) -> Scope:
    """Context manager to patch the scope for the starlette-admin app.

    Returns a copy of the original scope so that any modification to the scope made by the Starlette
    application does not affect components of the Litestar application that have already taken
    a reference to it.

    We also adjust the request path by appending the admin base URL. As we mount the `asgi` handler
    in Litestar to the admin base URL, Litestar strips that value from the path in scope. However,
    we must configure the starlette-admin base path to the same path as we have mounted the handler
    so that any url generation in starlette-admin will work correctly. That is, if we were to set the base
    URL in the admin app to `/`, then any calls to `url_for` in starlette-admin would generate URLs
    without the base URL, which would not work correctly.

    Args:
        scope: The ASGI scope.
        mount_path: The base URL for the admin app.

    Yields:
        The patched scope.
    """
    copied_scope = cast("Scope", dict(scope))
    copied_scope["path"] = f"{mount_path}{scope['path']}"
    return copied_scope
