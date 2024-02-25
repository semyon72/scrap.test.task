## Автоматизація дампа та експорту таблиці в Docker контейнері

### Утворення та запуск контейнеру

1. Утворюємо image
````
docker build -t scrap_postgres -f Dockerfile-scrap-postgres --progress plain .
````
> Якщо треба спостерігати детальний лог утворення image без використання cache
````
docker build -t scrap_postgres -f Dockerfile-scrap-postgres --progress plain --no-cache . 
````
> Якщо треба змінити місце розташування скриптів на хост машині 
````
docker build -t scrap_postgres_cron --build-arg="HOST_DOT_ENV=./app/.env" --build-arg "HOST_SCRIPT_DIR=./dockerized_cron/" -f dockerized_cron/Dockerfile-scrap-postgres --progress plain .
````

2. Утворити та виконати container

````
docker run -p 5432:5432 --name scrap_postgres_cron_server scrap_postgres_cron
````  

або з використанням Volumes та монтуванням тек контейнеру в теки хосту

> Перед тим як виконати наступну команду необхідно утворити теки ./exports та ./dumps на хості та надати привілеї іншим
писати. Відповідні шляхи до тек в середині контейнера повинні відповідати зазначеним в CRON_DUMP_DIR та CRON_EXPORT_DIR
Docker файлу.
````
docker run -p 5432:5432 -v 88162b58d23097e1d99ddbe32890404c0a0ac3ac48e96ec056f1fd959210c3ff:/var/lib/postgresql/data -v ./exports:/cron/exports -v ./dumps:/cron/dumps --name scrap_postgres_server --rm scrap_postgres
````
> 88162b58d23097e1d99ddbe32890404c0a0ac3ac48e96ec056f1fd959210c3ff - volume до вже існуючої PostgreSQL з даними  
> Для заполбігання використанню '88162b58d23097e1d99ddbe32890404c0a0ac3ac48e96ec056f1fd959210c3ff'
можливо, попередньо, утворити іменовані Volumes. Для прикладу
````
docker volume create scrap_postgres_data
````
> де будуть зберігатись файли БД
````
docker volume create scrap_db_dumps
````
> де будуть складатись SQL dump файли

## Корисні команди
> Почистити images що не використовуються
````
docker builder prune -a
````
> Доєднатись до контейнеру
````
docker exec -it scrap_postgres_server /bin/bash
````
> Зупинити контейнер
````
docker container stop scrap_postgres_server
````
> Стартанути контейнер
````
docker container start scrap_postgres_server
````
> Переглянути log контейнеру
````
docker logs scrap_postgres_server
````

### Переваги та недоліки

#### Переваги
1. Семантично dump та export відносяться до завдань що мають бути розгорнуті на сервері.
Що найменш з причини відповідності версії PostgreSQL клієнта -> серверу. Що є за замовчанням на сервері.
2. Відсутнє навантаження на мережу у випадку великих обсягів даних.
3. Є можливість зробити "холодну" копію.

#### Недоліки
1. Все необхідно імплементувати в Bash або Perl, що є в наявності в PostgreSQL зображені за замовчанням.
Все інше необхідно буде довстановлювати.
2. Скрипти на Bash - легковажна, гарна річ але не є достатньо гнучкою.
Для прикладу - завантаження .env файлу критично до ' ' між '=', коментарів або заміни раніш використаних зміних ...
А отже - обмежені можливості, залежність від правильності форматування файлу або призводить до ускладнення bash скрипту.
Хоча для Bash (Perl) "гуру" може й саме ОНО.  

### Приклад роботи

```
Starting periodic command scheduler: cron.

PostgreSQL Database directory appears to contain a database; Skipping initialization

2024-02-24 10:49:24.549 UTC [1] LOG:  starting PostgreSQL 16.1 (Debian 16.1-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit
2024-02-24 10:49:24.549 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2024-02-24 10:49:24.549 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2024-02-24 10:49:24.551 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2024-02-24 10:49:24.556 UTC [53] LOG:  database system was interrupted; last known up at 2024-02-24 10:37:29 UTC
2024-02-24 10:49:24.610 UTC [53] LOG:  database system was not properly shut down; automatic recovery in progress
2024-02-24 10:49:24.612 UTC [53] LOG:  redo starts at 0/1D98FB8
2024-02-24 10:49:24.612 UTC [53] LOG:  invalid record length at 0/1D98FF0: expected at least 24, got 0
2024-02-24 10:49:24.612 UTC [53] LOG:  redo done at 0/1D98FB8 system usage: CPU: user: 0.00 s, system: 0.00 s, elapsed: 0.00 s
2024-02-24 10:49:24.616 UTC [51] LOG:  checkpoint starting: end-of-recovery immediate wait
2024-02-24 10:49:24.624 UTC [51] LOG:  checkpoint complete: wrote 3 buffers (0.0%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.003 s, sync=0.001 s, total=0.009 s; sync files=2, longest=0.001 s, average=0.001 s; distance=0 kB, estimate=0 kB; lsn=0/1D98FF0, redo lsn=0/1D98FF0
2024-02-24 10:49:24.628 UTC [1] LOG:  database system is ready to accept connections
Sat Feb 24 10:50:01 UTC 2024: I am alive.
  adding: - (deflated 72%)
2024-02-24_10:50:01: export into /cron/exports/export-2024-02-24.zip is successful.
Sat Feb 24 10:51:01 UTC 2024: I am alive.
Sat Feb 24 10:52:01 UTC 2024: I am alive.
  adding: - (deflated 70%)
2024-02-24_10:52:01: dump into /cron/dumps/dump-2024-02-24.zip is successful.
Sat Feb 24 10:53:01 UTC 2024: I am alive.
```

> Розпис cron завдань захардкожен в Docker файлі :(