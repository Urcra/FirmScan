package main

import (
	"log"

	"github.com/streadway/amqp"
)

type TaskQueue struct {
	consume <-chan amqp.Delivery
	publish chan []byte
}


func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}


func newTaskQueue(username, password, location, port, publishName, consumeName string) *TaskQueue {
	// Connect to RabbitMQ
	conn, err := amqp.Dial("amqp://" + username + ":" + password + "@" + location + ":" + port + "/")
	failOnError(err, "Failed to connect to RabbitMQ")

	// Setup publish channel
	publishChannel, err := conn.Channel()
	failOnError(err, "Failed to open a channel")

	publishQueue, err := publishChannel.QueueDeclare(
		publishName,    // name
		false,         // durable
		false,        // delete when unused
		false,        // exclusive
		false,        // no-wait
		nil,          // arguments
	)
	failOnError(err, "Failed to declare a queue")

	var publish = make(chan []byte)
	go func (){
		for msg := range publish {
			err := publishChannel.Publish(
				"",     // exchange
				publishQueue.Name, // routing key
				false,  // mandatory
				false,
				amqp.Publishing{
					DeliveryMode: amqp.Persistent,
					ContentType:  "text/plain",
					Body:         msg,
				})
			failOnError(err, "Failed to publish a message")
		}
	}()

	// Setup consume channel
	consumeChannel, err := conn.Channel()
	failOnError(err, "Failed to open a channel")

	consumeQueue, err := consumeChannel.QueueDeclare(
		consumeName,    // name
		false,         // durable
		false,        // delete when unused
		false,        // exclusive
		false,        // no-wait
		nil,          // arguments
	)
	failOnError(err, "Failed to declare a queue")

    err = consumeChannel.Qos(
        1,     // prefetch count
        0,     // prefetch size
        false, // global
    )
    failOnError(err, "Failed to set QoS")

    consume, err := consumeChannel.Consume(
        consumeQueue.Name, // queue
        "",     // consumer
        true,  // auto-ack
        false,  // exclusive
        false,  // no-local
        false,  // no-wait
        nil,    // args
    )
    failOnError(err, "Failed to register a consumer")

	return &TaskQueue{consume, publish}
}

/*
func (tq TaskQueue) close(){
	tq.publishChannel.Close()
	tq.consumeChannel.Close()
	tq.conn.Close()
}
*/
