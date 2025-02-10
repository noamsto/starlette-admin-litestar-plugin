# Starlette Admin Litestar Plugin

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![Litestar](https://img.shields.io/badge/Litestar-2.14+-yellow)](https://litestar.dev)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A plugin that integrates [Starlette Admin](https://jowilf.github.io/starlette-admin/) with [Litestar](https://litestar.dev/), providing a powerful and flexible admin interface for your Litestar applications.

This project is inspired by and based on [SQLAdmin Litestar Plugin](https://github.com/peterschutt/sqladmin-litestar-plugin) by Peter Schutt.

## Features

- Seamless integration with [Starlette Admin](https://jowilf.github.io/starlette-admin/)
- Support for both sync and async SQLAlchemy engines
- Advanced Alchemy integration with UUID7 support
- Customizable admin interface
- Authentication support
- I18n support

## Installation

```bash
pip install starlette-admin-litestar-plugin
```

## Basic Usage

```python
from litestar import Litestar
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from starlette_admin.contrib.sqla import ModelView
from starlette_admin_litestar_plugin import StarlettAdminPluginConfig, StarletteAdminPlugin

# Create engine and models
engine = create_async_engine("sqlite+aiosqlite:///:memory:")

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[int]

# Configure admin
admin_config = StarlettAdminPluginConfig(
    views=[ModelView(Product)],
    engine=engine,
    title="My Admin",
)

# Create app
app = Litestar(
    plugins=[StarletteAdminPlugin(starlette_admin_config=admin_config)]
)
```

## Advanced Alchemy Support! Usage with UUID7 Models

```python
from advanced_alchemy.base import UUIDv7AuditBase
from pydantic import BaseModel, Field
from starlette_admin_litestar_plugin.ext.advanced_alchemy import UUIDModelView

# Define model with UUID and audit
class Product(UUIDv7AuditBase):
    __tablename__ = "products"
    name: Mapped[str]
    price: Mapped[int]

# Optional: Add validation
class ProductInput(BaseModel):
    name: str = Field(..., max_length=100)
    price: int = Field(..., ge=0)

# Configure admin with UUID support
admin_config = StarlettAdminPluginConfig(
    views=[UUIDModelView(Product, pydantic_model=ProductInput)],
    engine=engine,
    title="Advanced Admin",
)

app = Litestar(
    plugins=[StarletteAdminPlugin(starlette_admin_config=admin_config)]
)
```

See [advanced-alchemy](https://github.com/litestar-org/advanced-alchemy) repo for more info.

## Configuration Options

| Option        | Type                  | Description                 | Default  |
| ------------- | --------------------- | --------------------------- | -------- |
| views         | Sequence[ModelView]   | List of admin views         | []       |
| engine        | Engine \| AsyncEngine | SQLAlchemy engine           | Required |
| title         | str                   | Admin interface title       | "Admin"  |
| base_url      | str                   | Base URL path               | "/admin" |
| auth_provider | BaseAuthProvider      | Authentication provider     | None     |
| i18n_config   | I18nConfig            | Internationalization config | None     |

For more configuration options and features, please refer to the [Starlette Admin documentation](https://jowilf.github.io/starlette-admin/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
