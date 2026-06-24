@"
FROM php:8.2-apache

RUN a2dismod mpm_event mpm_worker 2>/dev/null || true && \
    a2enmod mpm_prefork rewrite && \
    docker-php-ext-install pdo pdo_mysql

COPY . /var/www/html/

RUN chown -R www-data:www-data /var/www/html
"@ | Out-File -FilePath "C:\xampp\htdocs\Proyecto filmin\Dockerfile" -Encoding UTF8
