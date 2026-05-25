from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings

from models.base import Base


engine = create_async_engine(
    url=settings.database.url,
    echo=settings.database.echo
)

session_factory = async_sessionmaker(engine, expire_on_commit=False)


from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncConnection

async def insert_default_roles(connection: AsyncConnection):
    """Добавляет стандартные роли в базу данных"""
    
    # Проверяем, есть ли уже роли
    from sqlalchemy import text
    
    result = await connection.execute(
        text("SELECT COUNT(*) FROM roles")
    )
    count = result.scalar()
    
    if count == 0:
        # Добавляем стандартные роли
        await connection.execute(
            text("""
                INSERT INTO roles (code) VALUES 
                ('patient'),
                ('doctor'),
                ('dev'),
                ('admin');
            """)
        )
        print("✅ Default roles added successfully")
    else:
        print(f"ℹ️ Roles already exist ({count} roles found)")


# Модифицированная функция create_tables
async def create_tables():
    async with engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
        
        # Добавляем начальные роли
        await insert_default_roles(conn)
        await conn.commit()  # Фиксируем изменения


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)