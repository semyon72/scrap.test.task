# scrap.test.task
Web scraping - Тестове завдання

## Зміни
1. Автоматизацію виконання імплементовано за допомогою [schedule](https://schedule.readthedocs.io/en/stable/)
   1. Всі атрибути доступні в Job доступні для конфігурації
   2. .env містить декілька прикладів з коментарями
2. Багато параметрів із .env минулої версії не сумісні з поточною
3. .pid файл не використовується
4. Додано logging (коментарі в .env)
5. Параметри POSTGRES_VERSION, POSTGRES_OS_CODENAME та PGDATA - не використовуються на безпосередньо в application,
а синхронізують Docker клієнта в application з Docker PostgreSQL сервером.
   > POSTGRES_VERSION=16.1 вказаний в .env використано для кешування (присутній в мене).
   > Для запуску, якщо ще не було підтягнуто жодного image PostgreSQL краще вказувати 15, 14, 13, ...  
6. POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB - Використовуються для налагодження БД для використання DB_CONFIG_*
   > після того як перевірено наявність користувача та бази даних (утворюється за необхідності) надалі використовуються
   > DB_CONFIG_HOST, DB_CONFIG_PORT, DB_CONFIG_PASSWORD, DB_CONFIG_USERNAME, DB_CONFIG_DATABASE
7. Додано Dockerfile та docker-compose.yml 
   > DB_CONFIG_HOST в .env зазначено у відповідності до docker-compose.yml 

## Інструкція з розгортання (Linux)
1. Перейдіть до теки де плануєте встановити застосунок 
   ```
      $ cd some_dir/ 
   ```
2. Клонуйте з Git
   ```
      $ git clone https://github.com/semyon72/scrap.test.task.git
   ```
3. Перейдіть до утвореної теки з назвою `scrap.test.task` в середині `some_dir`
   ```
      $ cd scrap.test.task
   ```
4. Ініціалізуйте Python virtual environment
   ```
       ...some_dir/scrap.test.task$ python3 -m venv .venv 
   ```
5. Активізуйте virtual environment
   ```
       $ source .venv/bin/activate 
   ```

6. Всатновіть необхідні packages з requirements.txt
   ```
       (.venv) ... $ pip install -r requirements.txt
   ```
   > Перед запуском застосунку необхідно мати встановлений та налогоджений PostgreSQL сервер та заповнений відповідним чином `.env` файл (опис нижче) 

7. Застосунок запускається за допомогою виконання `main.py`
   ```
       (.venv) ... $ python main.py
   або
       /bin/bash --verbose -c 'cd /.../scrap.test.task/app; source ../.venv/bin/activate && python main.py'
   або
       cd /.../scrap.test.task/app; source ../.venv/bin/activate && python main.py    
   ```  

## .env

### Налагодження бази даних
- DB_CONFIG_USERNAME=scrap_test_task_user
- DB_CONFIG_PASSWORD=12345678
- DB_CONFIG_HOST=localhost_or_postrgesql_service_name_from_compose_file
> Якщо отримано помилку на кшталт
> `psql: error: connection to server at "db" (172.26.0.2), port 5432 failed: FATAL:  password authentication failed for user "scrap_test_task_user"
2024-03-03T16:16:51.870459510Z`
> Це означає, що scraper жодного разу не виконувався і перевірка наявності бази даних і таблиці не виконувалась.
> одразу як scraper буде виконано - все одразу налагодиться
- DB_CONFIG_PORT=5432
- DB_CONFIG_DATABASE=scrap_test_task

- DB_ECHO=False  # Виводить в консоль всі SQL маніпуляції (True - для спостерігання логів на LOGGING_LEVEL нижчому за INFO)
- DB_DROP_TABLE=False # True - Видаляє таблицю, перед тим як утворити нову, False - Використовується існуюча або утворюється нова якщо не існує.    

### Налагодження парсингу
- ROOT_URL=https://auto.ria.com/car/used/  # entrypoint  
- URL_PAGE_PARM_NAME=page  # query parameter що ідентифікує сторінку
- PAGE_START=12  # сторінка початку (включно)
> Можливо вказувати будь-яке позитивне int але не більше ніж вказане в PAGE_END   
- PAGE_END=15  # сторінка кінця (включно)
> Можливо вказувати будь-яке int значення одразу як сторінка з таким номером поверне 404 або результат парсингу не дасть жодного посилання на авто - робота буде завершеною
- SLEEP_AFTER_REQUEST=0  # час затримки між витребуванням сторінок
> Час затримки - Float значення в секундах і відповідає лише за одну ітерацію - інтервал між отриманням сторінки з посиланнями на дані щодо автомобілів.  
- DUMPS_DIR = './dumps'  # тека де зберігаються backup-s таблиці
> В теці вже присутній один архів для прикладу. Кожний запуск застосунку (на самому початку) генерує zip файл для поточного дня. У випадку декількох запусків протягом дня в zip додається окремий файл з часовою міткою. Дані з таблиці експортуються в csv фармат. 

### Налагодження періодичного виконання (Sсheduler)

- SCHEDTAB_XXX - дозволяє конфігурувати окремі правила (Jobs) подібно crontab
> Дозволеними ключами є всі, що підтримуються schedule.Job об'єктом
- Ключ 'do' є обов'язковим, а значення залежить від імплементації в коді.
> Поточно підтримувані значення 'to_csv', 'dump', 'scrap', 'alive'
- Ключ 'run_once' за замовчанням є False (буде запускатись періодично)
- Приклади
```
# Just for testing purpoces. Will send 'I am alive' in console on DEBUG level
SCHEDTAB_ALIVE="
    do=alive,
    minutes=1
"

SCHEDTAB_EXPORT="
    do=to_csv,
    minutes=1,
    until=2024-03-05 18:57,
    run_once=true
"
```

## Примітки
> Тека `work` містить лише робочі матеріали та може бути видалена. 
 
### Приклад логу
```
2024-03-03T16:22:28.691846328Z [2024-03-03 16:22:28,691]:app:INFO:Starting
2024-03-03T16:22:28.691931619Z [2024-03-03 16:22:28,691]:app:INFO:	Active job#0#Job(interval=1, unit=minutes, do=to_csv, args=(), kwargs={})
2024-03-03T16:22:28.692000044Z [2024-03-03 16:22:28,691]:app:INFO:	Active job#1#Job(interval=1, unit=minutes, do=wrapper, args=(), kwargs={})
2024-03-03T16:22:28.692067220Z [2024-03-03 16:22:28,691]:app:INFO:	Active job#2#Job(interval=1, unit=days, do=scrap, args=(), kwargs={})
2024-03-03T16:22:28.692292949Z [2024-03-03 16:22:28,692]:app:INFO:	Active job#3#Job(interval=1, unit=minutes, do=dump, args=(), kwargs={})
2024-03-03T16:23:28.751040481Z [2024-03-03 16:23:28,750]:app:INFO:run function [to_csv]
2024-03-03T16:23:28.857461766Z psql: error: connection to server at "db" (172.26.0.2), port 5432 failed: FATAL:  password authentication failed for user "scrap_test_task_user"
2024-03-03T16:23:28.859236425Z [2024-03-03 16:23:28,859]:app:INFO:function [to_csv] done in 0.109sec.
2024-03-03T16:23:28.859446225Z [2024-03-03 16:23:28,859]:app:INFO:Cancelling job for function [to_csv]. Decorated by [run_once].
2024-03-03T16:23:28.859600001Z [2024-03-03 16:23:28,859]:app:INFO:run function [functools.partial(<bound method Logger.debug of <Logger app (INFO)>>, 'I am alive')]
2024-03-03T16:23:28.859612440Z [2024-03-03 16:23:28,859]:app:INFO:function [functools.partial(<bound method Logger.debug of <Logger app (INFO)>>, 'I am alive')] done in 0.0sec.
2024-03-03T16:23:28.859753413Z [2024-03-03 16:23:28,859]:app:INFO:run function [dump]
2024-03-03T16:23:28.914923125Z pg_dump: error: connection to server at "db" (172.26.0.2), port 5432 failed: FATAL:  password authentication failed for user "scrap_test_task_user"
2024-03-03T16:23:28.916661732Z [2024-03-03 16:23:28,916]:app:INFO:function [dump] done in 0.057sec.
2024-03-03T16:24:28.918366355Z [2024-03-03 16:24:28,918]:app:INFO:	Active job#0#Job(interval=1, unit=minutes, do=wrapper, args=(), kwargs={})
2024-03-03T16:24:28.918436305Z [2024-03-03 16:24:28,918]:app:INFO:	Active job#1#Job(interval=1, unit=days, do=scrap, args=(), kwargs={})
2024-03-03T16:24:28.918446351Z [2024-03-03 16:24:28,918]:app:INFO:	Active job#2#Job(interval=1, unit=minutes, do=dump, args=(), kwargs={})
2024-03-03T16:24:28.918688213Z [2024-03-03 16:24:28,918]:app:INFO:run function [functools.partial(<bound method Logger.debug of <Logger app (INFO)>>, 'I am alive')]
2024-03-03T16:24:28.918700233Z [2024-03-03 16:24:28,918]:app:INFO:function [functools.partial(<bound method Logger.debug of <Logger app (INFO)>>, 'I am alive')] done in 0.0sec.
2024-03-03T16:24:28.919028003Z [2024-03-03 16:24:28,918]:app:INFO:run function [dump]
2024-03-03T16:24:28.975811983Z pg_dump: error: connection to server at "db" (172.26.0.2), port 5432 failed: FATAL:  password authentication failed for user "scrap_test_task_user"
2024-03-03T16:24:28.977571186Z [2024-03-03 16:24:28,977]:app:INFO:function [dump] done in 0.059sec.
2024-03-03T16:25:00.032531338Z [2024-03-03 16:25:00,030]:app:INFO:run function [scrap]
2024-03-03T16:25:03.722273933Z [2024-03-03 16:25:03,722]:sqlalchemy.engine.Engine:INFO:select pg_catalog.version()
2024-03-03T16:25:03.722515932Z [2024-03-03 16:25:03,722]:sqlalchemy.engine.Engine:INFO:[raw sql] {}
2024-03-03T16:25:03.724756152Z [2024-03-03 16:25:03,724]:sqlalchemy.engine.Engine:INFO:select current_schema()
2024-03-03T16:25:03.724791102Z [2024-03-03 16:25:03,724]:sqlalchemy.engine.Engine:INFO:[raw sql] {}
2024-03-03T16:25:03.726151638Z [2024-03-03 16:25:03,725]:sqlalchemy.engine.Engine:INFO:show standard_conforming_strings
2024-03-03T16:25:03.726185987Z [2024-03-03 16:25:03,725]:sqlalchemy.engine.Engine:INFO:[raw sql] {}
2024-03-03T16:25:03.730942326Z [2024-03-03 16:25:03,730]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit; DBAPI should not BEGIN due to autocommit mode)
2024-03-03T16:25:03.731011992Z [2024-03-03 16:25:03,730]:sqlalchemy.engine.Engine:INFO:SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower(%(database)s);
2024-03-03T16:25:03.731129571Z [2024-03-03 16:25:03,730]:sqlalchemy.engine.Engine:INFO:[generated in 0.00029s] {'database': 'scrap_test_task'}
2024-03-03T16:25:03.733975118Z [2024-03-03 16:25:03,732]:sqlalchemy.engine.Engine:INFO:SELECT usename FROM pg_catalog.pg_user WHERE lower(usename) = lower(%(username)s);
2024-03-03T16:25:03.734011330Z [2024-03-03 16:25:03,733]:sqlalchemy.engine.Engine:INFO:[generated in 0.00022s] {'username': 'scrap_test_task_user'}
2024-03-03T16:25:03.736163506Z [2024-03-03 16:25:03,735]:sqlalchemy.engine.Engine:INFO:CREATE USER scrap_test_task_user PASSWORD '12345678'
2024-03-03T16:25:03.736191015Z [2024-03-03 16:25:03,735]:sqlalchemy.engine.Engine:INFO:[generated in 0.00026s] {}
2024-03-03T16:25:03.748930649Z [2024-03-03 16:25:03,748]:sqlalchemy.engine.Engine:INFO:CREATE DATABASE scrap_test_task WITH OWNER=scrap_test_task_user
2024-03-03T16:25:03.749072860Z [2024-03-03 16:25:03,748]:sqlalchemy.engine.Engine:INFO:[generated in 0.00020s] {}
2024-03-03T16:25:03.818018657Z [2024-03-03 16:25:03,817]:sqlalchemy.engine.Engine:INFO:select pg_catalog.version()
2024-03-03T16:25:03.818100065Z [2024-03-03 16:25:03,817]:sqlalchemy.engine.Engine:INFO:[raw sql] {}
2024-03-03T16:25:03.819482479Z [2024-03-03 16:25:03,819]:sqlalchemy.engine.Engine:INFO:select current_schema()
2024-03-03T16:25:03.819669399Z [2024-03-03 16:25:03,819]:sqlalchemy.engine.Engine:INFO:[raw sql] {}
2024-03-03T16:25:03.820852125Z [2024-03-03 16:25:03,820]:sqlalchemy.engine.Engine:INFO:show standard_conforming_strings
2024-03-03T16:25:03.820882414Z [2024-03-03 16:25:03,820]:sqlalchemy.engine.Engine:INFO:[raw sql] {}
2024-03-03T16:25:03.823885660Z [2024-03-03 16:25:03,823]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:03.827647121Z [2024-03-03 16:25:03,827]:sqlalchemy.engine.Engine:INFO:SELECT pg_catalog.pg_class.relname 
2024-03-03T16:25:03.827679198Z FROM pg_catalog.pg_class JOIN pg_catalog.pg_namespace ON pg_catalog.pg_namespace.oid = pg_catalog.pg_class.relnamespace 
2024-03-03T16:25:03.827687539Z WHERE pg_catalog.pg_class.relname = %(table_name)s::VARCHAR AND pg_catalog.pg_class.relkind = ANY (ARRAY[%(param_1)s::VARCHAR, %(param_2)s::VARCHAR, %(param_3)s::VARCHAR, %(param_4)s::VARCHAR, %(param_5)s::VARCHAR]) AND pg_catalog.pg_table_is_visible(pg_catalog.pg_class.oid) AND pg_catalog.pg_namespace.nspname != %(nspname_1)s::VARCHAR
2024-03-03T16:25:03.827724085Z [2024-03-03 16:25:03,827]:sqlalchemy.engine.Engine:INFO:[generated in 0.00022s] {'table_name': 'ria_used_cars', 'param_1': 'r', 'param_2': 'p', 'param_3': 'f', 'param_4': 'v', 'param_5': 'm', 'nspname_1': 'pg_catalog'}
2024-03-03T16:25:03.830634357Z [2024-03-03 16:25:03,830]:sqlalchemy.engine.Engine:INFO:
2024-03-03T16:25:03.830662833Z CREATE TABLE ria_used_cars (
2024-03-03T16:25:03.830670831Z 	id SERIAL NOT NULL, 
2024-03-03T16:25:03.830676961Z 	url VARCHAR NOT NULL, 
2024-03-03T16:25:03.830682748Z 	title VARCHAR NOT NULL, 
2024-03-03T16:25:03.830687370Z 	price_usd INTEGER NOT NULL, 
2024-03-03T16:25:03.830692201Z 	odometer INTEGER NOT NULL, 
2024-03-03T16:25:03.830697657Z 	username VARCHAR NOT NULL, 
2024-03-03T16:25:03.830702217Z 	phone_number BIGINT NOT NULL, 
2024-03-03T16:25:03.830706859Z 	image_url VARCHAR NOT NULL, 
2024-03-03T16:25:03.830711454Z 	images_count INTEGER NOT NULL, 
2024-03-03T16:25:03.830716310Z 	car_number VARCHAR(30) NOT NULL, 
2024-03-03T16:25:03.830721891Z 	car_vin VARCHAR(30) NOT NULL, 
2024-03-03T16:25:03.830726944Z 	datetime_found DATE DEFAULT CURRENT_DATE NOT NULL, 
2024-03-03T16:25:03.830733688Z 	PRIMARY KEY (id)
2024-03-03T16:25:03.830739205Z )
2024-03-03T16:25:03.830743996Z 
2024-03-03T16:25:03.830748756Z 
2024-03-03T16:25:03.830845924Z [2024-03-03 16:25:03,830]:sqlalchemy.engine.Engine:INFO:[no key 0.00014s] {}
2024-03-03T16:25:03.837061495Z [2024-03-03 16:25:03,836]:sqlalchemy.engine.Engine:INFO:CREATE UNIQUE INDEX ix_ria_used_cars_url ON ria_used_cars (url)
2024-03-03T16:25:03.837126505Z [2024-03-03 16:25:03,837]:sqlalchemy.engine.Engine:INFO:[no key 0.00026s] {}
2024-03-03T16:25:03.839484407Z [2024-03-03 16:25:03,839]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:03.842489678Z [2024-03-03 16:25:03,842]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:03.844623017Z [2024-03-03 16:25:03,844]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:03.844652848Z FROM ria_used_cars 
2024-03-03T16:25:03.844660329Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:03.844666163Z [2024-03-03 16:25:03,844]:sqlalchemy.engine.Engine:INFO:[generated in 0.00018s] {'url_1': 'https://auto.ria.com/uk/auto_bmw_3_series_36118731.html'}
2024-03-03T16:25:03.848833032Z [2024-03-03 16:25:03,848]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:03.848875378Z [2024-03-03 16:25:03,848]:sqlalchemy.engine.Engine:INFO:[generated in 0.00023s] {'url': 'https://auto.ria.com/uk/auto_bmw_3_series_36118731.html', 'title': 'BMW 3 Series 2018', 'price_usd': 25800, 'odometer': 36000, 'username': 'Ярослав', 'phone_number': 997568362, 'image_url': 'https://cdn3.riastatic.com/photosnew/auto/photo/bmw_3-series__538731863f.jpg', 'images_count': 22, 'car_number': 'BE6665CA', 'car_vin': 'WBA8E1C59JA762821', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:03.851119333Z [2024-03-03 16:25:03,850]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:05.056241192Z [2024-03-03 16:25:05,056]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:05.056688540Z [2024-03-03 16:25:05,056]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:05.056709562Z FROM ria_used_cars 
2024-03-03T16:25:05.056715767Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:05.056888882Z [2024-03-03 16:25:05,056]:sqlalchemy.engine.Engine:INFO:[cached since 1.212s ago] {'url_1': 'https://auto.ria.com/uk/auto_byd_song_plus_champion_36102417.html'}
2024-03-03T16:25:05.059803402Z [2024-03-03 16:25:05,059]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:05.060040632Z [2024-03-03 16:25:05,059]:sqlalchemy.engine.Engine:INFO:[cached since 1.211s ago] {'url': 'https://auto.ria.com/uk/auto_byd_song_plus_champion_36102417.html', 'title': 'BYD Song Plus Champion 2023', 'price_usd': 32800, 'odometer': 1000, 'username': 'SKM-1 Kyiv', 'phone_number': 675464141, 'image_url': 'https://cdn2.riastatic.com/photosnew/auto/photo/byd_song-plus-champion__538287717f.jpg', 'images_count': 36, 'car_number': '', 'car_vin': 'LGXCE4CB2P0550462', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:05.061753549Z [2024-03-03 16:25:05,061]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:06.180575892Z [2024-03-03 16:25:06,180]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:06.181761895Z [2024-03-03 16:25:06,181]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:06.181811132Z FROM ria_used_cars 
2024-03-03T16:25:06.181827410Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:06.182271606Z [2024-03-03 16:25:06,181]:sqlalchemy.engine.Engine:INFO:[cached since 2.337s ago] {'url_1': 'https://auto.ria.com/uk/auto_honda_m_nv_36038974.html'}
2024-03-03T16:25:06.190402377Z [2024-03-03 16:25:06,190]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:06.190796529Z [2024-03-03 16:25:06,190]:sqlalchemy.engine.Engine:INFO:[cached since 2.342s ago] {'url': 'https://auto.ria.com/uk/auto_honda_m_nv_36038974.html', 'title': 'Honda M-NV 2023', 'price_usd': 21780, 'odometer': 1000, 'username': 'SKM-1 Київ', 'phone_number': 673729773, 'image_url': 'https://cdn4.riastatic.com/photosnew/auto/photo/honda_m-nv__536603419f.jpg', 'images_count': 25, 'car_number': '', 'car_vin': 'LVHDH2863P5003102', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:06.193770371Z [2024-03-03 16:25:06,193]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:06.634091080Z [2024-03-03 16:25:06,633]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:06.634480378Z [2024-03-03 16:25:06,634]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:06.634498094Z FROM ria_used_cars 
2024-03-03T16:25:06.634505549Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:06.634660969Z [2024-03-03 16:25:06,634]:sqlalchemy.engine.Engine:INFO:[cached since 2.79s ago] {'url_1': 'https://auto.ria.com/uk/auto_toyota_land_cruiser_prado_35930153.html'}
2024-03-03T16:25:06.637151475Z [2024-03-03 16:25:06,636]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:06.637210527Z [2024-03-03 16:25:06,637]:sqlalchemy.engine.Engine:INFO:[cached since 2.789s ago] {'url': 'https://auto.ria.com/uk/auto_toyota_land_cruiser_prado_35930153.html', 'title': 'Toyota Land Cruiser Prado 2010', 'price_usd': 24999, 'odometer': 215000, 'username': 'AutoPlus', 'phone_number': 955050006, 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/toyota_land-cruiser-prado__533693025f.jpg', 'images_count': 92, 'car_number': '', 'car_vin': 'JTEBH3FJx05xxxx25', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:06.638507045Z [2024-03-03 16:25:06,638]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:08.065466578Z [2024-03-03 16:25:08,065]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:08.065841185Z [2024-03-03 16:25:08,065]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:08.065859545Z FROM ria_used_cars 
2024-03-03T16:25:08.065865379Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:08.066074458Z [2024-03-03 16:25:08,065]:sqlalchemy.engine.Engine:INFO:[cached since 4.222s ago] {'url_1': 'https://auto.ria.com/uk/auto_tesla_model_s_36135370.html'}
2024-03-03T16:25:08.071433731Z [2024-03-03 16:25:08,071]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:08.071656332Z [2024-03-03 16:25:08,071]:sqlalchemy.engine.Engine:INFO:[cached since 4.223s ago] {'url': 'https://auto.ria.com/uk/auto_tesla_model_s_36135370.html', 'title': 'Tesla Model S 2014', 'price_usd': 16999, 'odometer': 73000, 'username': 'AutoPlus', 'phone_number': 955050006, 'image_url': 'https://cdn4.riastatic.com/photosnew/auto/photo/tesla_model-s__539182839f.jpg', 'images_count': 73, 'car_number': 'BH8881MM', 'car_vin': '5YJSA1CN4DFP18810', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:08.072902081Z [2024-03-03 16:25:08,072]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:08.620163137Z [2024-03-03 16:25:08,620]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:08.620606336Z [2024-03-03 16:25:08,620]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:08.620643101Z FROM ria_used_cars 
2024-03-03T16:25:08.620656157Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:08.620662384Z [2024-03-03 16:25:08,620]:sqlalchemy.engine.Engine:INFO:[cached since 4.776s ago] {'url_1': 'https://auto.ria.com/uk/auto_tesla_model_y_36154414.html'}
2024-03-03T16:25:08.623054686Z [2024-03-03 16:25:08,622]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:08.623290433Z [2024-03-03 16:25:08,622]:sqlalchemy.engine.Engine:INFO:[cached since 4.774s ago] {'url': 'https://auto.ria.com/uk/auto_tesla_model_y_36154414.html', 'title': 'Tesla Model Y 2023', 'price_usd': 36300, 'odometer': 39000, 'username': 'Oleg', 'phone_number': 631215999, 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/tesla_model-y__539726740f.jpg', 'images_count': 29, 'car_number': '', 'car_vin': '', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:08.624638903Z [2024-03-03 16:25:08,624]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:10.218502742Z [2024-03-03 16:25:10,218]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:10.219067655Z [2024-03-03 16:25:10,218]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:10.219090867Z FROM ria_used_cars 
2024-03-03T16:25:10.219098164Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:10.219189613Z [2024-03-03 16:25:10,219]:sqlalchemy.engine.Engine:INFO:[cached since 6.375s ago] {'url_1': 'https://auto.ria.com/uk/auto_land_rover_range_rover_35330947.html'}
2024-03-03T16:25:10.221686072Z [2024-03-03 16:25:10,221]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:10.221914853Z [2024-03-03 16:25:10,221]:sqlalchemy.engine.Engine:INFO:[cached since 6.373s ago] {'url': 'https://auto.ria.com/uk/auto_land_rover_range_rover_35330947.html', 'title': 'Land Rover Range Rover 2010', 'price_usd': 15950, 'odometer': 166000, 'username': 'Владислав', 'phone_number': 731101712, 'image_url': 'https://cdn2.riastatic.com/photosnew/auto/photo/land-rover_range-rover__517712167f.jpg', 'images_count': 43, 'car_number': 'BH1712PT', 'car_vin': 'SALMF1E47AA323256', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:10.223417973Z [2024-03-03 16:25:10,223]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:10.737803733Z [2024-03-03 16:25:10,737]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:10.738379569Z [2024-03-03 16:25:10,738]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:10.738419744Z FROM ria_used_cars 
2024-03-03T16:25:10.738429048Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:10.738566955Z [2024-03-03 16:25:10,738]:sqlalchemy.engine.Engine:INFO:[cached since 6.894s ago] {'url_1': 'https://auto.ria.com/uk/auto_volkswagen_tiguan_36152480.html'}
2024-03-03T16:25:10.740348989Z [2024-03-03 16:25:10,740]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:10.740643995Z [2024-03-03 16:25:10,740]:sqlalchemy.engine.Engine:INFO:[cached since 6.892s ago] {'url': 'https://auto.ria.com/uk/auto_volkswagen_tiguan_36152480.html', 'title': 'Volkswagen Tiguan 2019', 'price_usd': 19800, 'odometer': 86000, 'username': 'Василь Васильйович Соловій', 'phone_number': 982522977, 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/volkswagen_tiguan__539672481f.jpg', 'images_count': 24, 'car_number': '', 'car_vin': '3VV1B7AX8KM055381', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:10.741819932Z [2024-03-03 16:25:10,741]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:11.254820016Z [2024-03-03 16:25:11,254]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:11.255244325Z [2024-03-03 16:25:11,255]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:11.255274416Z FROM ria_used_cars 
2024-03-03T16:25:11.255298921Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:11.255311823Z [2024-03-03 16:25:11,255]:sqlalchemy.engine.Engine:INFO:[cached since 7.411s ago] {'url_1': 'https://auto.ria.com/uk/auto_skoda_kodiaq_36148359.html'}
2024-03-03T16:25:11.257248552Z [2024-03-03 16:25:11,257]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:11.257518947Z [2024-03-03 16:25:11,257]:sqlalchemy.engine.Engine:INFO:[cached since 7.409s ago] {'url': 'https://auto.ria.com/uk/auto_skoda_kodiaq_36148359.html', 'title': 'Skoda Kodiaq 2018', 'price_usd': 24700, 'odometer': 160000, 'username': 'IZI AUTO LUTSK', 'phone_number': 970102233, 'image_url': 'https://cdn4.riastatic.com/photosnew/auto/photo/skoda_kodiaq__539551544f.jpg', 'images_count': 109, 'car_number': '', 'car_vin': 'TMBJJ9NS7J8067018', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:11.259791913Z [2024-03-03 16:25:11,259]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:11.704824449Z [2024-03-03 16:25:11,704]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:11.705325448Z [2024-03-03 16:25:11,705]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:11.705360173Z FROM ria_used_cars 
2024-03-03T16:25:11.705372569Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:11.705505840Z [2024-03-03 16:25:11,705]:sqlalchemy.engine.Engine:INFO:[cached since 7.861s ago] {'url_1': 'https://auto.ria.com/uk/auto_bmw_5_series_36062092.html'}
2024-03-03T16:25:11.708255372Z [2024-03-03 16:25:11,707]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:11.708783394Z [2024-03-03 16:25:11,708]:sqlalchemy.engine.Engine:INFO:[cached since 7.86s ago] {'url': 'https://auto.ria.com/uk/auto_bmw_5_series_36062092.html', 'title': 'BMW 5 Series 2019', 'price_usd': 41900, 'odometer': 61000, 'username': 'Саша', 'phone_number': 960007070, 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/bmw_5-series__537208630f.jpg', 'images_count': 39, 'car_number': '', 'car_vin': 'WBAJR71000WW55447', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:11.710580532Z [2024-03-03 16:25:11,710]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:13.239542967Z [2024-03-03 16:25:13,239]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:13.239942433Z [2024-03-03 16:25:13,239]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:13.239972561Z FROM ria_used_cars 
2024-03-03T16:25:13.240070602Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:13.240082190Z [2024-03-03 16:25:13,239]:sqlalchemy.engine.Engine:INFO:[cached since 9.396s ago] {'url_1': 'https://auto.ria.com/uk/auto_ford_focus_36146024.html'}
2024-03-03T16:25:13.242017449Z [2024-03-03 16:25:13,241]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:13.242094778Z [2024-03-03 16:25:13,241]:sqlalchemy.engine.Engine:INFO:[cached since 9.393s ago] {'url': 'https://auto.ria.com/uk/auto_ford_focus_36146024.html', 'title': 'Ford Focus 2012', 'price_usd': 8700, 'odometer': 219000, 'username': 'Yaroslav', 'phone_number': 934866680, 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/ford_focus__539483326f.jpg', 'images_count': 86, 'car_number': '', 'car_vin': '', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:13.243318001Z [2024-03-03 16:25:13,243]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:13.673638663Z [2024-03-03 16:25:13,672]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:13.674749322Z [2024-03-03 16:25:13,674]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:13.674817426Z FROM ria_used_cars 
2024-03-03T16:25:13.674837123Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:13.675151004Z [2024-03-03 16:25:13,674]:sqlalchemy.engine.Engine:INFO:[cached since 9.83s ago] {'url_1': 'https://auto.ria.com/uk/auto_bmw_3_series_35938387.html'}
2024-03-03T16:25:13.680272255Z [2024-03-03 16:25:13,679]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:13.680584519Z [2024-03-03 16:25:13,680]:sqlalchemy.engine.Engine:INFO:[cached since 9.832s ago] {'url': 'https://auto.ria.com/uk/auto_bmw_3_series_35938387.html', 'title': 'BMW 3 Series 2001', 'price_usd': 5500, 'odometer': 285000, 'username': 'Микола', 'phone_number': 978167824, 'image_url': 'https://cdn4.riastatic.com/photosnew/auto/photo/bmw_3-series__533914759f.jpg', 'images_count': 11, 'car_number': 'BH4891PK', 'car_vin': 'WBABS110X0JX63559', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:13.683413144Z [2024-03-03 16:25:13,683]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:14.950281729Z [2024-03-03 16:25:14,950]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:14.950667075Z [2024-03-03 16:25:14,950]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:14.950682807Z FROM ria_used_cars 
2024-03-03T16:25:14.950689710Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:14.950797560Z [2024-03-03 16:25:14,950]:sqlalchemy.engine.Engine:INFO:[cached since 11.11s ago] {'url_1': 'https://auto.ria.com/uk/auto_honda_ens1_36102662.html'}
2024-03-03T16:25:14.952399835Z [2024-03-03 16:25:14,952]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:14.952564601Z [2024-03-03 16:25:14,952]:sqlalchemy.engine.Engine:INFO:[cached since 11.1s ago] {'url': 'https://auto.ria.com/uk/auto_honda_ens1_36102662.html', 'title': 'Honda eNS1 2023', 'price_usd': 23200, 'odometer': 1000, 'username': 'SKM-1 Київ', 'phone_number': 673729773, 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/honda_ens1__538294566f.jpg', 'images_count': 28, 'car_number': '', 'car_vin': 'LVHRS1853P5202845', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:14.953918965Z [2024-03-03 16:25:14,953]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:15.466105551Z [2024-03-03 16:25:15,465]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:15.466531123Z [2024-03-03 16:25:15,466]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:15.466563653Z FROM ria_used_cars 
2024-03-03T16:25:15.466570426Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:15.466806408Z [2024-03-03 16:25:15,466]:sqlalchemy.engine.Engine:INFO:[cached since 11.62s ago] {'url_1': 'https://auto.ria.com/uk/auto_volkswagen_tiguan_35922172.html'}
2024-03-03T16:25:15.469237511Z [2024-03-03 16:25:15,469]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:15.469475281Z [2024-03-03 16:25:15,469]:sqlalchemy.engine.Engine:INFO:[cached since 11.62s ago] {'url': 'https://auto.ria.com/uk/auto_volkswagen_tiguan_35922172.html', 'title': 'Volkswagen Tiguan 2016', 'price_usd': 16500, 'odometer': 125000, 'username': 'Ruslan', 'phone_number': 989363449, 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/volkswagen_tiguan__533480605f.jpg', 'images_count': 19, 'car_number': 'BO9779CE', 'car_vin': 'WVGBV7AX4GW607813', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:15.470885224Z [2024-03-03 16:25:15,470]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:18.080497364Z [2024-03-03 16:25:18,080]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:18.168001163Z [2024-03-03 16:25:18,167]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:18.168040075Z FROM ria_used_cars 
2024-03-03T16:25:18.168048937Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:18.168304546Z [2024-03-03 16:25:18,167]:sqlalchemy.engine.Engine:INFO:[cached since 14.32s ago] {'url_1': 'https://auto.ria.com/uk/auto_honda_m_nv_35465154.html'}
2024-03-03T16:25:18.170985357Z [2024-03-03 16:25:18,170]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:18.171480761Z [2024-03-03 16:25:18,171]:sqlalchemy.engine.Engine:INFO:[cached since 14.32s ago] {'url': 'https://auto.ria.com/uk/auto_honda_m_nv_35465154.html', 'title': 'Honda M-NV 2022', 'price_usd': 23100, 'odometer': 1000, 'username': 'Bex Auto', 'phone_number': 730946478, 'image_url': 'https://cdn4.riastatic.com/photosnew/auto/photo/honda_m-nv__521188174f.jpg', 'images_count': 33, 'car_number': '', 'car_vin': 'LVHDH287XN5009069', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:18.174566402Z [2024-03-03 16:25:18,174]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:18.665088159Z [2024-03-03 16:25:18,664]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:18.665505542Z [2024-03-03 16:25:18,665]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:18.665523137Z FROM ria_used_cars 
2024-03-03T16:25:18.665529394Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:18.665720953Z [2024-03-03 16:25:18,665]:sqlalchemy.engine.Engine:INFO:[cached since 14.82s ago] {'url_1': 'https://auto.ria.com/uk/auto_renault_master_36084477.html'}
2024-03-03T16:25:18.667866233Z [2024-03-03 16:25:18,667]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:18.668037114Z [2024-03-03 16:25:18,667]:sqlalchemy.engine.Engine:INFO:[cached since 14.82s ago] {'url': 'https://auto.ria.com/uk/auto_renault_master_36084477.html', 'title': 'Renault Master 2016', 'price_usd': 11500, 'odometer': 900000, 'username': 'Діма Сидорук', 'phone_number': 951456522, 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/renault_master__537823970f.jpg', 'images_count': 13, 'car_number': 'AC4246EO', 'car_vin': 'VF1VB000056805015', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:18.669242610Z [2024-03-03 16:25:18,669]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:19.213250520Z [2024-03-03 16:25:19,213]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:19.213673871Z [2024-03-03 16:25:19,213]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:19.213723752Z FROM ria_used_cars 
2024-03-03T16:25:19.213735688Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:19.213885307Z [2024-03-03 16:25:19,213]:sqlalchemy.engine.Engine:INFO:[cached since 15.37s ago] {'url_1': 'https://auto.ria.com/uk/auto_volkswagen_passat_36082517.html'}
2024-03-03T16:25:19.216337729Z [2024-03-03 16:25:19,216]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:19.216525518Z [2024-03-03 16:25:19,216]:sqlalchemy.engine.Engine:INFO:[cached since 15.37s ago] {'url': 'https://auto.ria.com/uk/auto_volkswagen_passat_36082517.html', 'title': 'Volkswagen Passat 2021', 'price_usd': 24200, 'odometer': 142000, 'username': 'Михайло Михайлович', 'phone_number': 995629717, 'image_url': 'https://cdn1.riastatic.com/photosnew/auto/photo/volkswagen_passat__537769891f.jpg', 'images_count': 67, 'car_number': '', 'car_vin': 'WVWZZZ3CZME062474', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:19.217968985Z [2024-03-03 16:25:19,217]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:20.192374554Z [2024-03-03 16:25:20,191]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:20.193352640Z [2024-03-03 16:25:20,192]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:20.193401206Z FROM ria_used_cars 
2024-03-03T16:25:20.193420491Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:20.193878142Z [2024-03-03 16:25:20,193]:sqlalchemy.engine.Engine:INFO:[cached since 16.35s ago] {'url_1': 'https://auto.ria.com/uk/auto_honda_m_nv_36053013.html'}
2024-03-03T16:25:20.199462666Z [2024-03-03 16:25:20,198]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:20.200097250Z [2024-03-03 16:25:20,199]:sqlalchemy.engine.Engine:INFO:[cached since 16.35s ago] {'url': 'https://auto.ria.com/uk/auto_honda_m_nv_36053013.html', 'title': 'Honda M-NV 2023', 'price_usd': 21780, 'odometer': 1000, 'username': 'Батарейка іК', 'phone_number': 634100907, 'image_url': 'https://cdn3.riastatic.com/photosnew/auto/photo/honda_m-nv__536960573f.jpg', 'images_count': 15, 'car_number': '', 'car_vin': 'LVHDH2868P5000753', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:20.206946766Z [2024-03-03 16:25:20,206]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:20.603448512Z [2024-03-03 16:25:20,603]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:20.603896034Z [2024-03-03 16:25:20,603]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:20.603922114Z FROM ria_used_cars 
2024-03-03T16:25:20.603931928Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:20.604008743Z [2024-03-03 16:25:20,603]:sqlalchemy.engine.Engine:INFO:[cached since 16.76s ago] {'url_1': 'https://auto.ria.com/uk/auto_byd_song_plus_champion_35667799.html'}
2024-03-03T16:25:20.606050610Z [2024-03-03 16:25:20,605]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:20.606130041Z [2024-03-03 16:25:20,605]:sqlalchemy.engine.Engine:INFO:[cached since 16.76s ago] {'url': 'https://auto.ria.com/uk/auto_byd_song_plus_champion_35667799.html', 'title': 'BYD Song Plus Champion 2023', 'price_usd': 32800, 'odometer': 1000, 'username': '4Колеса', 'phone_number': 630608621, 'image_url': 'https://cdn4.riastatic.com/photosnew/auto/photo/byd_song-plus-champion__526593239f.jpg', 'images_count': 24, 'car_number': '', 'car_vin': 'LGXCE4CB9P0449418', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:20.607478286Z [2024-03-03 16:25:20,607]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:21.073771623Z [2024-03-03 16:25:21,073]:sqlalchemy.engine.Engine:INFO:BEGIN (implicit)
2024-03-03T16:25:21.074323323Z [2024-03-03 16:25:21,074]:sqlalchemy.engine.Engine:INFO:SELECT ria_used_cars.id AS ria_used_cars_id, ria_used_cars.url AS ria_used_cars_url, ria_used_cars.title AS ria_used_cars_title, ria_used_cars.price_usd AS ria_used_cars_price_usd, ria_used_cars.odometer AS ria_used_cars_odometer, ria_used_cars.username AS ria_used_cars_username, ria_used_cars.phone_number AS ria_used_cars_phone_number, ria_used_cars.image_url AS ria_used_cars_image_url, ria_used_cars.images_count AS ria_used_cars_images_count, ria_used_cars.car_number AS ria_used_cars_car_number, ria_used_cars.car_vin AS ria_used_cars_car_vin, ria_used_cars.datetime_found AS ria_used_cars_datetime_found 
2024-03-03T16:25:21.074365142Z FROM ria_used_cars 
2024-03-03T16:25:21.074374127Z WHERE ria_used_cars.url = %(url_1)s::VARCHAR FOR UPDATE
2024-03-03T16:25:21.074837323Z [2024-03-03 16:25:21,074]:sqlalchemy.engine.Engine:INFO:[cached since 17.23s ago] {'url_1': 'https://auto.ria.com/uk/auto_nissan_leaf_36157815.html'}
2024-03-03T16:25:21.077172445Z [2024-03-03 16:25:21,076]:sqlalchemy.engine.Engine:INFO:INSERT INTO ria_used_cars (url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found) VALUES (%(url)s::VARCHAR, %(title)s::VARCHAR, %(price_usd)s::INTEGER, %(odometer)s::INTEGER, %(username)s::VARCHAR, %(phone_number)s::BIGINT, %(image_url)s::VARCHAR, %(images_count)s::INTEGER, %(car_number)s::VARCHAR, %(car_vin)s::VARCHAR, %(datetime_found)s::DATE) RETURNING ria_used_cars.id
2024-03-03T16:25:21.077441425Z [2024-03-03 16:25:21,077]:sqlalchemy.engine.Engine:INFO:[cached since 17.23s ago] {'url': 'https://auto.ria.com/uk/auto_nissan_leaf_36157815.html', 'title': 'Nissan Leaf 2012', 'price_usd': 6700, 'odometer': 88000, 'username': 'Роман', 'phone_number': 986533346, 'image_url': 'https://cdn0.riastatic.com/photosnew/auto/photo/nissan_leaf__539822115f.jpg', 'images_count': 38, 'car_number': '', 'car_vin': '', 'datetime_found': datetime.date(2024, 3, 3)}
2024-03-03T16:25:21.078759012Z [2024-03-03 16:25:21,078]:sqlalchemy.engine.Engine:INFO:COMMIT
2024-03-03T16:25:21.087175744Z [2024-03-03 16:25:21,086]:app:INFO:function [scrap] done in 21.057sec.
2024-03-03T16:25:28.926491584Z [2024-03-03 16:25:28,926]:app:INFO:run function [functools.partial(<bound method Logger.debug of <Logger app (INFO)>>, 'I am alive')]
2024-03-03T16:25:28.926655983Z [2024-03-03 16:25:28,926]:app:INFO:function [functools.partial(<bound method Logger.debug of <Logger app (INFO)>>, 'I am alive')] done in 0.0sec.
2024-03-03T16:25:28.978634523Z [2024-03-03 16:25:28,978]:app:INFO:run function [dump]
2024-03-03T16:25:29.122300079Z [2024-03-03 16:25:29,122]:app:INFO:function [dump] done in 0.144sec.
2024-03-03T16:26:28.986893252Z [2024-03-03 16:26:28,986]:app:INFO:run function [functools.partial(<bound method Logger.debug of <Logger app (INFO)>>, 'I am alive')]
2024-03-03T16:26:28.987746772Z [2024-03-03 16:26:28,986]:app:INFO:function [functools.partial(<bound method Logger.debug of <Logger app (INFO)>>, 'I am alive')] done in 0.0sec.
2024-03-03T16:26:29.124115826Z [2024-03-03 16:26:29,123]:app:INFO:run function [dump]
2024-03-03T16:26:29.282111386Z [2024-03-03 16:26:29,281]:app:INFO:function [dump] done in 0.158sec.
```

