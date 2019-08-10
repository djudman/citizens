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
- Запустите тесты  
    `$ make test`  

`TODO:`

Установка на сервер
-------------------
1. Установите на сервер необходимое ПО:
    - nginx >= 1.14.0  
        - `$ sudo apt-get install nginx`
    - mongodb >= 4.0.12  
        - https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
    - supervisor >= 3.3.1  
        - `$ sudo apt-get install supervisor`

2. Скачайте архив с исходным кодом:  
`$ wget http://<domain.com>/citizens.tar.gz`
3. Перейти в директорию с исходными файлами и выполнить команду для установки:  
`$ cd citizens && make install`  
    - В процессе установки некоторые команды выполняются с `sudo`, поэтому ваш пользователь
    должен быть в группе `sudoers`, а также, вам скорее всего потребуется ввести ваш пароль.
4. Запустить сервис  
`$ make start`  
5. Сделать тестовый запрос и убедиться, что ответ получен  

Примеры тестовых запросов:  

`$ curl -X POST --data '[{"citizen_id": 1,"town": "Москва","street": "Льва Толстого","building": "16к7стр5","apartment": 7,"name": "Иванов Сергей Иванович","birth_date": "17.04.1999","gender": "male","relatives": []}]' http://0.0.0.0:8080/imports`  
  
`$ curl -X GET http://0.0.0.0:8080/imports/1/citizens`  

`$ curl -X GET http://0.0.0.0:8080/imports/1/citizens/birthdays`  

`$ curl -X GET http://0.0.0.0:8080/imports/1/towns/stat/percentile/age`  

`$ curl -X PATCH --data '{"apartment": 777}' http://0.0.0.0:8080/imports/1/citizens/1`  

`TODO:`

Зависимости
-----------
- aiohttp 3.5.4
- pymongo 3.8.0
- numpy 1.17.0


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

Разработка и тестирование велись с использованием **Python 3.7.3**.  
Скорее всего всё будет работать и на более младших версиях Python ( >= 3.5.3),
но из-за ограниченности времени, тестирование на других версиях не проводилось.

 `TODO:`
