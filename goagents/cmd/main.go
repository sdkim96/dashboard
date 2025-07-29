package main

import (
	"fmt"
	"io"
	"time"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	// Define your routes here
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})

	r.POST("/api/v1/stream", func(c *gin.Context) {

		// Handle the streaming request here
		c.Stream(func(w io.Writer) bool {
			// Simulate streaming data
			for i := 0; i < 10; i++ {
				fmt.Fprintf(w, "data: %d\n\n", i)
				time.Sleep(1 * time.Second) // Simulate delay
			}
			return false // Stop streaming
		})
	})

	// Start the server
	if err := r.Run(); err != nil {
		panic(err)
	}
}
