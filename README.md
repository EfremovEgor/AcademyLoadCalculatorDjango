
## Описание
Веб-приложен написанное на Python(FastAPI), HTML, CSS, JS, использующееся для вычисления нагрузки на преподавателя, просмотра предметов. Написано для Инженерной академии Российского Университета Дружбы Народов.
## Clone repo
    git clone https://github.com/EfremovEgor/AcademyLoadCalculatorFastApi.git
    pip install -r requirements.txt
    
## Run Dev
Создать ./.env и заполнить его:

    DJANGO_DATABASE_HOST=host
    DJANGO_DATABASE_PORT=port
    DJANGO_DATABASE_NAME=name
    DJANGO_DATABASE_USER=user
    DJANGO_DATABASE_PASSWORD=password
    DJANGO_SECRET_KEY=key
    DEBUG = 1
Запустить проект:

	cd /src
    python manage.py runserver

## Run Prod
Заполнить под себя:

 ./env-production  
 ./docker-compose.yaml
./nginx/nginx.conf

	docker compose up —build -d

    
## Скриншоты
![login page](https://imgur.com/DUbtIWv.png)
![enter image description here](https://i.imgur.com/82V06pu.png)
![enter image description here](https://i.imgur.com/Npc7uxV.png)
![enter image description here](https://i.imgur.com/OPrhdZB.png)
![enter image description here](https://i.imgur.com/FLAypbU.png)
![enter image description here](https://i.imgur.com/4Ujxp2v.png)
![enter image description here](https://i.imgur.com/1kUlh7g.png)
![enter image description here](https://i.imgur.com/PB90hKJ.png)