FROM wordpress:php8.3-apache
RUN apt-get update && apt-get install -y --no-install-recommends libicu-dev libzip-dev libxml2-dev unzip \
    && docker-php-ext-install bcmath intl pdo_mysql \
    && rm -rf /var/lib/apt/lists/*
COPY --from=wordpress:cli-php8.3 /usr/local/bin/wp /usr/local/bin/wp
COPY php.ini /usr/local/etc/php/conf.d/labg.ini
