package main

import (
	"log"

	"github.com/streadway/amqp"
)

type TaskQueue struct {
	conn *amqp.Connection
	channel *amqp.Channel
	queue amqp.Queue
}


func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

func newTaskQueue(username, password, location, port, queueName string) *TaskQueue {
	conn, err := amqp.Dial("amqp://" + username + ":" + password + "@" + location + ":" + port + "/")
	failOnError(err, "Failed to connect to RabbitMQ")

	channel, err := conn.Channel()
	failOnError(err, "Failed to open a channel")

	queue, err := channel.QueueDeclare(
		queueName,    // name
		true,         // durable
		false,        // delete when unused
		false,        // exclusive
		false,        // no-wait
		nil,          // arguments
	)
	failOnError(err, "Failed to declare a queue")

	return &TaskQueue{conn, channel, queue}
}


func (tq TaskQueue) publish(msg []byte) {
	err := tq.channel.Publish(
		"",     // exchange
		tq.queue.Name, // routing key
		false,  // mandatory
		false,
		amqp.Publishing{
			DeliveryMode: amqp.Persistent,
			ContentType:  "text/plain",
			Body:         msg,
		})
	failOnError(err, "Failed to publish a message")
}


func (tq TaskQueue) close(){
	tq.channel.Close()
	tq.conn.Close()
}