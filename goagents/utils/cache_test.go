package utils

import (
	"fmt"
	"sync"
	"testing"
)

func TestSave(t *testing.T) {
	cache := NewVectorCache()
	wg := sync.WaitGroup{}
	wg.Add(10)

	for i := 0; i < 10; i++ {
		go func(i int) {
			defer wg.Done()
			vector := []float64{1.0, 2.0, 3.0}
			id := fmt.Sprintf("test-vector-%d", i)

			cache.Save(id, vector)
		}(i)
	}

	wg.Wait()

	for i := 0; i < 10; i++ {
		savedVector, exists := cache.Get(fmt.Sprintf("test-vector-%d", i))
		if !exists {
			t.Errorf("Expected vector to be saved, but it was not found")
		}
		fmt.Printf("Vector for id %d: %v\n", i, savedVector)
	}

}
