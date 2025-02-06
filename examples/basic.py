from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from starlette_admin.contrib.sqla import ModelView

from starlette_admin_litestar_plugin import StarlettAdminPluginConfig, StarletteAdminPlugin

engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///:memory:")


class Base(DeclarativeBase):
    pass


class Store(Base):
    __tablename__ = "stores"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))


class Product(Base):
    __tablename__ = "products"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer())
    store_id: Mapped[UUID] = mapped_column(ForeignKey("stores.id"))
    store: Mapped[Store] = relationship("Store")


@asynccontextmanager
async def lifespan(_app: Litestar):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup on shutdown
    await engine.dispose()


admin_config = StarlettAdminPluginConfig(
    views=[ModelView(Product), ModelView(Store)],
    engine=engine,
    title="Simple Admin",
    base_url="/admin",
)

app = Litestar(
    plugins=[
        SQLAlchemyPlugin(
            config=SQLAlchemyAsyncConfig(engine_instance=engine, create_all=False)
        ),  # Set create_all to False since we handle it in lifespan
        StarletteAdminPlugin(starlette_admin_config=admin_config),
    ],
    lifespan=[lifespan],
)
