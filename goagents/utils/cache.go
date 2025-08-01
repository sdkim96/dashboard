package utils

import (
	"sync"
)

type EmbeddingCacheI interface {
	Save(id string, vector []float64) error
	Get(id string) ([]float64, bool)
}

type LocalEmbeddingCache struct {
	Cache map[string][]float64
	mu    sync.RWMutex
}

func NewVectorCache() *LocalEmbeddingCache {
	return &LocalEmbeddingCache{
		Cache: make(map[string][]float64),
	}
}

func (cache *LocalEmbeddingCache) Save(id string, vector []float64) error {
	cache.mu.Lock()
	defer cache.mu.Unlock()
	cache.Cache[id] = vector
	return nil
}

func (cache *LocalEmbeddingCache) Get(id string) ([]float64, bool) {
	cache.mu.RLock()
	defer cache.mu.RUnlock()
	vector, exists := cache.Cache[id]
	if !exists {
		return nil, false
	}
	return vector, true
}
