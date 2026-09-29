from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete
from config import DATABASE_URL
from database.models import Base, DateIdea

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Очищаем старые тестовые карточки, чтобы загрузить полные 20 штук
        await session.execute(delete(DateIdea))
        await session.commit()

        demo_ideas = [
            # ДОМАШНИЕ (10 штук)
            DateIdea(
                title="Вечер настолок и пиццы 🍕",
                description="Заказываем большую пиццу, включаем уютную музыку и устраиваем турнир в настолки.",
                location_type="home", weather_type="any", requirements_text="Купить пиццу", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1513151233558-d860c5398176?w=500"
            ),
            DateIdea(
                title="Домашний СПА-вечер 🧖‍♀️",
                description="Маски для лица, ванна с пеной, массаж с маслами и расслабляющий чай.",
                location_type="home", weather_type="any", requirements_text="Аромамасла, маски", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=500"
            ),
            DateIdea(
                title="Кулинарный баттл 👩‍🍳",
                description="Готовим вместе сложное ресторанное блюдо или крутим суши с нуля.",
                location_type="home", weather_type="any", requirements_text="Продукты по рецепту", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=500"
            ),
            DateIdea(
                title="Киномарафон с фортом 🏰",
                description="Строим форт из подушек и пледов, включаем франшизу (Гарри Поттер/Властелин Колец).",
                location_type="home", weather_type="any", requirements_text="Пледы, попкорн", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=500"
            ),
            DateIdea(
                title="Вечер рисования и вина 🍷",
                description="Берем холсты, краски и рисуем портреты друг друга под вино.",
                location_type="home", weather_type="any", requirements_text="Холсты, краски, вино", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=500"
            ),
            DateIdea(
                title="Слепая дегустация сыров 🧀",
                description="Покупаем 5 разных видов сыра и шоколада и угадываем с завязанными глазами.",
                location_type="home", weather_type="any", requirements_text="Разные виды сыра", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1452195100486-9cc805987862?w=500"
            ),
            DateIdea(
                title="Игровая ночь на консоли 🎮",
                description="Проходим парную игру (It Takes Two / Overcooked) на вылет.",
                location_type="home", weather_type="any", requirements_text="Геймпады, чипсы", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=500"
            ),
            DateIdea(
                title="Акустический вечер 🎸",
                description="Слушаем винил или каверы при свечах и пьем вкусный горячий напиток.",
                location_type="home", weather_type="any", requirements_text="Свечи", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500"
            ),
            DateIdea(
                title="Доска желаний (Vision Board) 🗺️",
                description="Вырезаем журналы, составляем общую коллаж-доску наших путешествий и целей.",
                location_type="home", weather_type="any", requirements_text="Журналы, клей, ватман", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=500"
            ),
            DateIdea(
                title="Пикник на балконе 🌌",
                description="Укутываемся в гирлянды и пледы, пьем какао под звёздами на балконе.",
                location_type="home", weather_type="any", requirements_text="Термос с какао", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?w=500"
            ),

            # ВНЕ ДОМА (10 штук)
            DateIdea(
                title="Закат на крыше / Смотровой 🌇",
                description="Берем термос с горячим чаем, плед и встречаем закат над городом.",
                location_type="outside", weather_type="sunny", requirements_text="Термос, тёплый плед", requires_booking=True,
                photo_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            ),
            DateIdea(
                title="Гончарная мастерская 🏺",
                description="Парный мастер-класс: лепим памятную посуду или кружки друг для друга.",
                location_type="outside", weather_type="indoor", requirements_text="Бронь мастер-класса", requires_booking=True,
                photo_url="https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=500"
            ),
            DateIdea(
                title="Прогулка на лошадях 🐎",
                description="Романтическая прогулка верхом по лесной тропе.",
                location_type="outside", weather_type="sunny", requirements_text="Удобная одежда", requires_booking=True,
                photo_url="https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=500"
            ),
            DateIdea(
                title="Поход в океанариум 🐠",
                description="Разглядываем скатов и акул в прозрачном туннеле.",
                location_type="outside", weather_type="indoor", requirements_text="Билеты", requires_booking=True,
                photo_url="https://images.unsplash.com/photo-1524704685729-29007e1916d9?w=500"
            ),
            DateIdea(
                title="Картинг и адреналин 🏎️",
                description="Устраиваем гонки на трассе, выясняем, кто из нас лучший гонщик.",
                location_type="outside", weather_type="any", requirements_text="Спортивная одежда", requires_booking=True,
                photo_url="https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=500"
            ),
            DateIdea(
                title="Свидание в планетарии 🪐",
                description="Смотрим на звёзды, туманности и галактики под огромным куполом.",
                location_type="outside", weather_type="indoor", requirements_text="Билеты", requires_booking=True,
                photo_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500"
            ),
            DateIdea(
                title="Джаз в уютном баре 🎷",
                description="Живой джазовый концерт, авторские коктейли и приглушенный свет.",
                location_type="outside", weather_type="indoor", requirements_text="Столик в баре", requires_booking=True,
                photo_url="https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=500"
            ),
            DateIdea(
                title="Пикник у водоема 🧺",
                description="Корзина с фруктами, круассанами, колонкой и покрывалом у воды.",
                location_type="outside", weather_type="sunny", requirements_text="Фрукты, покрывало", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1526772662000-3f88f10405ff?w=500"
            ),
            DateIdea(
                title="Винтажный маркет / Блошиный рынок 📻",
                description="Ищем странные штучки, редкие пластинки и старинные книги.",
                location_type="outside", weather_type="sunny", requirements_text="Наличные", requires_booking=False,
                photo_url="https://images.unsplash.com/photo-1531058020387-3be344556be6?w=500"
            ),
            DateIdea(
                title="Прогулка на лодке или SUP-ах 🚣‍♀️",
                description="Арендуем лодку или сапборды и плаваем на озере.",
                location_type="outside", weather_type="sunny", requirements_text="Сменная одежда", requires_booking=True,
                photo_url="https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=500"
            )
        ]
        session.add_all(demo_ideas)
        await session.commit()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session