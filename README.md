# Starlette Admin Litestar Plugin

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org)
[![Litestar](https://img.shields.io/badge/Litestar-2.14+-yellow)](https://litestar.dev)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Nix](https://img.shields.io/badge/Nix-5277C3?logo=nixos&logoColor=fff)](#)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A plugin that integrates [Starlette Admin](https://github.com/jowilf/starlette-admin) with [Litestar](https://litestar.dev/), providing a powerful and flexible admin interface for your Litestar applications.

## Features

- Seamless integration of Starlette Admin with Litestar
- Support for both sync and async SQLAlchemy engines
- Customizable admin interface (title, logo, templates, etc.)
- Internationalization support
- Authentication provider integration
- Custom view support

## Requirements

- Python >= 3.12
- Litestar >= 2.14.0
- Starlette Admin
- Advanced Alchemy >= 0.27.1

## Installation

```bash
pip install starlette-admin-litestar-plugin
```

## Quick Start

Here's a basic example of how to use the plugin:

```python
from litestar import Litestar
from starlette_admin_litestar_plugin import StarletteAdminPlugin, StarlettAdminPluginConfig
from starlette_admin.contrib.sqla import ModelView

# Define your SQLAlchemy models and views
class UserModel(Base):
    __tablename__ = "users"
    # ... model definition

class UserAdmin(ModelView):
    model = UserModel
    # ... view configuration

# Configure the plugin
admin_config = StarlettAdminPluginConfig(
    title="My Admin Interface",
    views=[UserAdmin()],
    engine=engine,  # Your SQLAlchemy engine
)

# Create Litestar app with the plugin
app = Litestar(
    plugins=[StarletteAdminPlugin(starlette_admin_config=admin_config)]
)
```

## Configuration

The `StarlettAdminPluginConfig` class supports the following options:

| Option         | Type                   | Description                   | Default  |
| -------------- | ---------------------- | ----------------------------- | -------- |
| views          | Sequence\[ModelView\]  | List of admin views           | \[\]     |
| engine         | Engine \| AsyncEngine  | SQLAlchemy engine instance    | Required |
| title          | str                    | Admin interface title         | "Admin"  |
| base_url       | str                    | Base URL path                 | "/admin" |
| route_name     | str                    | Name for admin route group    | None     |
| logo_url       | str                    | Header logo URL               | None     |
| login_logo_url | str                    | Login page logo URL           | None     |
| templates_dir  | str                    | Custom templates directory    | None     |
| statics_dir    | str                    | Custom static files directory | None     |
| index_view     | CustomView             | Custom index page view        | None     |
| auth_provider  | BaseAuthProvider       | Authentication provider       | None     |
| middlewares    | Sequence\[Middleware\] | Additional middlewares        | None     |
| debug          | bool                   | Enable debug mode             | False    |
| i18n_config    | I18nConfig             | Internationalization config   | None     |
| favicon_url    | str                    | Favicon URL                   | None     |

## Authentication

To add authentication to your admin interface:

```python
from starlette_admin.auth import AuthProvider

class MyAuthProvider(AuthProvider):
    async def login(self, username: str, password: str) -> bool:
        # Implement your login logic
        return True

    async def is_authenticated(self, request) -> bool:
        # Implement your authentication check
        return True

admin_config = StarlettAdminPluginConfig(
    # ... other config
    auth_provider=MyAuthProvider(),
)
```

## Custom Views

You can create custom views by extending `ModelView` or `CustomView`:

```python
from starlette_admin.contrib.sqla import ModelView

class CustomUserAdmin(ModelView):
    model = User
    fields = ["id", "username", "email"]
    fields_exclude = ["password"]
    search_fields = ["username", "email"]
    page_size = 25
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

Copyright 2024 Peter Schutt
Copyright 2025 Noam Stolero

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
