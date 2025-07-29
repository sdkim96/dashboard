package registry

import "github.com/openai/openai-go"

type EmbeddingStoreI interface {
	Embed(text string) ([]float64, error)
	EmbedBatch(texts []string) ([][]float64, error)
}

type OpenAIEmbeddingStore struct {
	Client *openai.Client
	Model  string
}
