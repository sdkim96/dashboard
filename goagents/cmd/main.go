package main

import (
	"fmt"
	"io"
	"time"

	"github.com/gin-gonic/gin"
	api "github.com/sdkim96/dashboard/apis"
)

type RecommendRequest struct {
	Query       string `json:"query"`
	UserContext string `json:"user_context"`
}

func main() {
	r := gin.Default()

	// Define your routes here
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})

	r.POST("/api/v1/recommend/agents", func(c *gin.Context) {
		var req RecommendRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		agents, err := api.RecommendAgents(req.Query, req.UserContext)
		if err != nil {
			c.JSON(500, gin.H{"message": "Failed to recommend agents", "error": err.Error()})
			return
		}

		c.JSON(200, gin.H{
			"message": "Agents recommended successfully",
			"agents":  agents,
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
