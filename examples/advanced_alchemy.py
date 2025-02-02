from __future__ import annotations

from uuid import UUID

from advanced_alchemy.base import UUIDv7AuditBase
from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship

from starlette_admin_litestar_plugin import StarlettAdminPluginConfig, StarletteAdminPlugin
from starlette_admin_litestar_plugin.ext.advanced_alchemy import UUIDModelView

# Setup async engine
engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///:memory:")


class Store(UUIDv7AuditBase):
    __tablename__ = "stores"

    name: Mapped[str] = mapped_column(String(100))


# Define model with UUID and audit
class Product(UUIDv7AuditBase):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer())
    store_id: Mapped[UUID] = mapped_column(ForeignKey("stores.id"))

    store: Mapped[Store] = relationship("Store")


# Optional: Add validation
class ProductInput(BaseModel):
    name: str = Field(..., max_length=100)
    price: int = Field(..., ge=0)


# Configure admin plugin
admin_config = StarlettAdminPluginConfig(
    views=[
        UUIDModelView(Product, pydantic_model=ProductInput),  # Optional custom validation
        UUIDModelView(Store),  # No custom validation
    ],
    engine=engine,
    title="Advanced Admin",
    base_url="/admin",
)

# Create app with plugins
app = Litestar(
    plugins=[
        SQLAlchemyPlugin(config=SQLAlchemyAsyncConfig(engine_instance=engine, create_all=True)),
        StarletteAdminPlugin(starlette_admin_config=admin_config),
    ]
)
