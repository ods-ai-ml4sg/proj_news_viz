
![](https://storage.yandexcloud.net/datasouls-ods/cache/0b/21/0b2195354066ea3d98da6c1a15de766d.jpg)  

Часть инициативы <img src="https://ods.ai/ods/logo/ml4sg.svg" width="30"> ML4SG от [ods.ai](https://ods.ai)

## Что здесь происходит
Мы делаем инструмент для исследования развития со временем [тем в текстах](www.machinelearning.ru/wiki/index.php?title=Тематическое_моделирование). Основной целевой набор текстов -- русскоязычные новости, но методика и сам инструмент подходят для произвольного набора текстов.  
  
Концепт такой:  
![Preview2](https://camo.githubusercontent.com/3f306e50fd0b38266da057dde30d010b2d511fe9/68747470733a2f2f692e6962622e636f2f526763736633762f6e6577732d76697a2d636f6e636570742e706e67)

### Ответы на все вопросы первым делом искать тут:  
https://github.com/ods-ai-ml4sg/proj_news_viz/wiki

Тут документация по основному коду https://github.com/ods-ai-ml4sg/proj_news_viz/wiki/Pipeline-инструкция-по-применению

## Структура репозитория  

```bash
.
├── README.md
├── pipeline           # текущая рабочая версия пайплайная, то есть основной код
├── visualization      # всячина связанная с визуализацией
├── scraping           # скрипты для скрапинга
├── nlp                # всё, что связано с nlp в проекте
│   ├──                # см. readme внутри
├── data-flow-luigi/nlp # зачатки продуктового пайплайна
├── data
│   ├── parsed         #  2018-09-28.json.txt -- список скачанных статей в json
│   └── parser
│       ├── articles   # 0/a1/0a1b2c3d.html.gz -- кеш скачанных страниц
│       ├── conf       # feeds.csv, sources.csv , ...
│       └── lists      # download_urls.txt , processed_urls.txt , ...
```



## Requirements

Python 3.6+

## Contributing

1. Сначала обсудите предлагаемые изменения в issues
2. Заводим ветку, в названии ветки лучше добавить свой ник, чтобы вас было легко найти, кодим-проверяем-коммитим
3. Создаем пулл-реквест

## Соглашения

1. Не стесняйтесь писать комменты на русском языке.
2. Пишите содержательные сообщения к коммитам.
3. Используйте black (https://github.com/psf/black) для автоматического форматирования кода.

## Чем вы можете помочь
1. Посмотрите issues -- там должны быть расписаны актуальные задачи
2. Помогите нам дополнить документацию и помочь другим разобраться в проекте
2. Если ничего не понятно -- задайте вопросы, это приветствуется

## Contributions
В алфавитном порядке

 - [@Alf162](https://github.com/Alf162)
 - [@Avenon](https://github.com/Avenon)
 - [@BoardGamer44](https://github.com/BoardGamer44)
 - [@Erlemar](https://github.com/Erlemar)
 - [@IlyaGusev](https://github.com/IlyaGusev)
 - [@LanSaid](https://github.com/LanSaid)
 - [@Midzay](https://github.com/Midzay)
 - [@Teoretic6](https://github.com/Teoretic6)
 - [@andreymalakhov](https://github.com/andreymalakhov)
 - [@aprotopopov](https://github.com/aprotopopov)
 - [@buriy](https://github.com/buriy)
 - [@darkzenon](https://github.com/darkzenon)
 - [@iggisv9t](https://github.com/iggisv9t)
 - [@m12sl](https://github.com/m12sl)
 - [@marishadorosh](https://github.com/marishadorosh)
 - [@monuvio](https://github.com/monuvio)
 - [@orech](https://github.com/orech)
 - [@p-kachalov](https://github.com/p-kachalov)
 - [@vtrokhymenko](https://github.com/vtrokhymenko)
 
Здесь могло быть ваше имя.
