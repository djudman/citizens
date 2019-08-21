# yandex-backend-school-rest-api
Вступительное задание для школы бэкенд разработки в Яндексе. REST API сервис.  
Формулировка задачи: https://yadi.sk/i/sw-6yNV0VBvZvQ

API
===
Реализованы следующие обработчики:
- **POST /imports**
- **PATCH /imports/`$import_id`/citizens/`$citizen_id`**
- **GET /imports/`$import_id`/citizens**
- **GET /imports/`import_id`/citizens/birthdays**
- **GET /imports/`$import_id`/towns/stat/percentile/age**

Установка
=========
Установка на локальную машину (для разработки/демонстрации/изучения)
--------------------------------------------------------------------
- Вам потребуется python 3.7.3  
(скорее всего, всё будет работать и на python >= 3.5.3, но я не проверял)  
  
- Скачайте архив с исходным кодом:  
    `wget https://storage.yandexcloud.net/yandex-backend-school/citizens-0.0.1.tar.gz`
- Извлеките содержимое архива  
    `tar -xzf citizens-0.0.1.tar.gz`
- Перейдите в извлеченную директорию  
    `cd citizens-0.0.1`
- Установите приложение  
    `python3 setup.py install`
- Запустите приложение  
    `python3 -m citizens`  
- Сервис будет запущен на порту `8080` на всех интерфейсах (`0.0.0.0`)  
- Сделайте тестовый запрос и убедись, что сервис работает:  
`curl -X POST --data '[{"citizen_id": 1,"town": "Москва","street": "Льва Толстого","building": "16к7стр5","apartment": 7,"name": "Иванов Сергей Иванович","birth_date": "17.04.1999","gender": "male","relatives": []}]' http://0.0.0.0:8080/imports`  


Установка на сервер
-------------------
1. Установите на сервер необходимое ПО:
    - nginx >= 1.14.0  
        - `sudo apt-get install nginx`
    - mongodb >= 4.0.12  
        - Инструкцию можно найти на их сайте:  
        https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/  
        Для удобства, приведу здесь список команд  
            - `wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | sudo apt-key add -`
            - `echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list`  
            - `sudo apt-get update`  
            - `sudo apt-get install -y mongodb-org`  
            - `sudo service mongod start`
    - supervisor >= 3.3.1  
        - `sudo apt-get install -y supervisor`
    - `sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv`  
    - make  
        - `sudo apt-get install make`

    - Для удобства, всё то же самое, но одной командой:  
        ```
        wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | sudo apt-key add -; \
        echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list; \
        sudo apt-get update; \
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mongodb-org nginx supervisor python3-venv make; \
        sudo service mongod start
        ```


2. Скачайте архив с исходным кодом:  
`wget https://storage.yandexcloud.net/yandex-backend-school/citizens-0.0.1.tar.gz`
3. Извлеките содержимое архива  
`tar -xzf citizens-0.0.1.tar.gz`
3. Перейдите в извлеченную директорию и выполните команду для установки:  
`cd citizens-0.0.1 && make install`  
    - В процессе установки некоторые команды выполняются с `sudo`, поэтому ваш пользователь
    должен быть в группе `sudoers`, а также, вам скорее всего потребуется ввести ваш пароль.
4. Cервис запущен. Попробуйте сделать тестовый запрос.
5. Если что-то пошло не так, смотрите логи.
    - /var/log/nginx/error.log
    - /var/log/supervisor/supervisor.log
    - ~/citizens-0.0.1/logs/citizens.log
    - ~/citizens-0.0.1/logs/supervisor_1_stdout.log (и/или supervisor_2_stdout.log)

Примеры тестовых запросов:  

- `curl -X POST --data '[{"citizen_id": 1,"town": "Москва","street": "Льва Толстого","building": "16к7стр5","apartment": 7,"name": "Иванов Сергей Иванович","birth_date": "17.04.1999","gender": "male","relatives": []}]' http://0.0.0.0:8080/imports`  
  
- `curl -X GET http://0.0.0.0:8080/imports/1/citizens`  

- `curl -X GET http://0.0.0.0:8080/imports/1/citizens/birthdays`  

- `curl -X GET http://0.0.0.0:8080/imports/1/towns/stat/percentile/age`  

- `curl -X PATCH --data '{"apartment": 777}' http://0.0.0.0:8080/imports/1/citizens/1`  

Зависимости
-----------
- aiohttp 3.5.4
- aiojobs 0.2.1
- pymongo 3.8.0
- numpy 1.17.0
  - Используется при подсчете перцентилей


Тестовый стенд
--------------
В систему установлены:

- python 3.7.3 (собран из исходных файлов, системный python не затронут)
- nginx 1.14.0 (из системных репозиторев)
- mongodb 4.0.12 (из репозитория repo.mongodb.org)
- supervisor 3.3.1 (из системных репозиторев)

Конфигурационные файлы для nginx и supervisor лежат в папке configs.  
В /etc/nginx/conf.d и в /etc/supervisor/conf.d созданы символические ссылки на эти файлы.  
Для mongodb используется конфиг по умолчанию.

Комментарии
-----------

- Разработка и тестирование велись с использованием **Python 3.7.3**.  
Скорее всего всё будет работать и на более младших версиях Python ( >= 3.5.3),
но из-за ограниченности времени, тестирование на других версиях не проводилось.

- Я осознанно не стал использовать библиотеку `marshmallow` для валидации входных
данных, потому что в моём тесте (`tests/test_marshmallow.py`) кастомная реализация
оказалась примерно в 4 раза быстрее.  
Хотя, конечно, кода гораздо меньше получается, если использовать marshmallow.

- Вы можете заметить по коммитам, что использовать регулярные выражения для 
проверки корректности формата даты, я стал использовать также из-за того, что
такой способ даёт прирост в скорости на тысячах записей (примерно x1.5)

- Я пробовал "стрелять" яндекс танком по сервису, развернутому на виртуалке в яндекс облаке  
    - Платформа: Intel Cascade Lake
    -  vCPU: 4
    -  Гарантированная доля vCPU: 5%
    -  RAM 4 ГБ
    -  HDD 5 ГБ  

    При таких условиях:
    - Кол-во жителей 10000
    - Схема нагрузки: const(10, 2m) (10 rps в течение 2х минут)  

    Вот такие результаты:
```
Percentiles (all/last 1m/last), ms:  . HTTP codes:
 100.0% <  4,310.0  4,310.0  2,046.4  . 1,143 +10  97.94% : 200 OK
  99.5% <  3,230.0  3,320.0  2,046.4  .    24  +0   2.06% : 201 Created
  99.0% <  2,810.0  3,090.0  1,939.5  .
  95.0% <  1,585.0  1,820.0  1,512.3  . Net codes:
  90.0% <  1,045.0  1,255.0    978.2  . 1,167 +10  100.00% :  0 Success
  85.0% <    775.0    925.0    788.5  .
  80.0% <    620.0    695.0    697.3  . Average Sizes (all/last), bytes:
  75.0% <    525.0    575.0    612.6  .  Request:  39,173.5 /     125.1
  70.0% <    449.0    485.0    481.0  . Response: 556,885.1 / 496,016.7
  60.0% <    327.0    362.0    452.0  .
  50.0% <    201.0    210.0    288.3  . Average Times (all/last), ms:
  40.0% <    113.0    122.0    111.0  . Overall: 416.61 / 489.28
  30.0% <     86.0     91.0     65.0  . Connect:  26.21 /  31.39
  20.0% <     68.0     74.0     50.0  .    Send:  14.78 /   0.07
  10.0% <     50.0     53.0     49.0  . Latency: 109.64 /  89.09
                                      . Receive: 265.99 / 368.73

 Cumulative Cases Info:
              name count       % last net_e http_e  avg ms last ms
          OVERALL: 1,167 100.00%  +10     0      0   416.6   489.2
    patch_citizen:   287  24.59%   +3     0      0    65.6    54.0
 get_all_citizens:   284  24.34%   +2     0      0   994.4 1,452.5
  get_percentiles:   287  24.59%   +2     0      0    98.0   117.5
    get_birthdays:   285  24.42%   +3     0      0   420.8   529.7
           import:    24   2.06%   +0     0      0 1,527.0     0.0
```

 `TODO:`
- дописать README.md
- написать как можно больше тестов на формат даты (объединить их в один)
- почитать тесты, написать еще юнит тестов
- при установке софта менять timezone на Europe/Moscow
- проверить, что сервис доступен из внутренней сети виртуалки на порту 8080

**стенд**
- поменять таймзону на стенде
- Установить сервис на стенд
- проверить, что сервис переживает перезагрузку ситемы и корректно поднимается
- пострелять танком по сервису на стенде
- почистить монгу на стенде

- docker. После запуска контейнера на 8080 сервис должен быть доступен
