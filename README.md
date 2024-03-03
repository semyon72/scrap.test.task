# scrap.test.task
Web scraping - Тестове завдання

## Зміни
1. Автоматизацію виконання імплементовано за допомогою [schedule](https://schedule.readthedocs.io/en/stable/)
   1. Всі атрибути доступні в Job доступні для конфігурації
   2. .env містить декілька прикладів з коментарями
2. Багато параметрів із .env минулої версії не сумісні з поточною
3. .pid файл не використовується
4. Додано logging (коментарі в .env)
5. Параметри POSTGRES_VERSION, POSTGRES_OS_CODENAME та PGDATA - не використовуються на пряму, а введені для сумісності з Docker PostgreSQL та майбутнього використання.
6. POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_DB - Використовуються для налагодження БД для використання DB_CONFIG_*
> після того як перевірено наявність користувача та бази даних (утворюється за необхідності) надалі використовуються
> DB_CONFIG_HOST, DB_CONFIG_PORT, DB_CONFIG_PASSWORD, DB_CONFIG_USERNAME, DB_CONFIG_DATABASE

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
- DB_CONFIG_HOST=localhost
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
 
