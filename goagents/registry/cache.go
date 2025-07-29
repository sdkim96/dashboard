package registry

import "sync"

type EmbeddingCache struct {
	Cache map[string][]float64
	mu    sync.RWMutex
}

func NewVectorCache() *EmbeddingCache {
	return &EmbeddingCache{
		Cache: make(map[string][]float64),
	}
}
func (cache *EmbeddingCache) Save(id string, vector []float64) {
	cache.mu.Lock()
	defer cache.mu.Unlock()
	cache.Cache[id] = vector
}

func (cache *EmbeddingCache) Get(id string) ([]float64, bool) {
	cache.mu.RLock()
	defer cache.mu.RUnlock()
	vector, exists := cache.Cache[id]
	return vector, exists
}
