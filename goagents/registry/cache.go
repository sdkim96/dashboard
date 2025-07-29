package registry

import "sync"

type EmbeddingCacheI interface {
	Save(id string, vector []float64)
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
func (cache *LocalEmbeddingCache) Save(id string, vector []float64) {
	cache.mu.Lock()
	defer cache.mu.Unlock()
	cache.Cache[id] = vector
}

func (cache *LocalEmbeddingCache) Get(id string) ([]float64, bool) {
	cache.mu.RLock()
	defer cache.mu.RUnlock()
	vector, exists := cache.Cache[id]
	return vector, exists
}
