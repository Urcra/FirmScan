docker run -d --hostname broker \
    -e RABBITMQ_ERLANG_COOKIE=6fghihH162 \
    -e RABBITMQ_DEFAULT_USER=broker \
    -e RABBITMQ_DEFAULT_PASS=xl65x7jhacv \
    -p 4369:4369 \
    -p 5671:5671 \
    -p 5672:5672 \
    -p 25672:25672 \
    --name rabbit rabbitmq:3
