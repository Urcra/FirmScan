package main

import (
	"fmt"
)

func reportCollector(taskQueue *TaskQueue) {
	for msg := range taskQueue.consume {
		fmt.Println(msg.Body)
	}
}
