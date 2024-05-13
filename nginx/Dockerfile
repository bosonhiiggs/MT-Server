FROM nginx

# Удалаем дефолтный файл конфигураций
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
# Создаем папки, в которых будут хранится статические и медиа файлы
RUN mkdir /musicTrainee
RUN mkdir /musicTrainee/static
RUN mkdir /musicTrainee/media

#RUN /etc/init.d/nginx restart
