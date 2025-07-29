package registry

import (
	"context"
	"fmt"
	"sync"

	openai "github.com/openai/openai-go"
)

type EmbeddingStoreI interface {
	Embed(text string) ([]float64, error)
	EmbedBatch(texts []string) ([][]float64, error)
}

type OpenAIEmbeddingStore struct {
	Client *openai.Client
}

func NewOpenAIEmbeddingStore(client *openai.Client) *OpenAIEmbeddingStore {
	return &OpenAIEmbeddingStore{
		Client: client,
	}
}

func (s *OpenAIEmbeddingStore) Embed(text string) ([]float64, error) {
	ctx := context.Background()
	resp, err := s.Client.Embeddings.New(
		ctx,
		openai.EmbeddingNewParams{
			Input: openai.EmbeddingNewParamsInputUnion{OfArrayOfStrings: []string{text}},
			Model: openai.EmbeddingModelTextEmbedding3Small,
		},
	)
	if err != nil {
		return nil, err
	}

	return resp.Data[0].Embedding, nil
}

func (s *OpenAIEmbeddingStore) EmbedBatch(texts []string) map[string][]float64 {

	wg := sync.WaitGroup{}
	vectorCh := make(chan map[string][]float64, len(texts))
	results := map[string][]float64{}

	wg.Add(len(texts))

	for _, text := range texts {
		go func(t string) {
			defer wg.Done()
			vector, err := s.Embed(t)
			if err != nil {
				vectorCh <- nil
				return
			}
			vectorCh <- map[string][]float64{t: vector}
		}(text)
	}
	wg.Wait()
	close(vectorCh)

	for embedding := range vectorCh {
		for k, v := range embedding {
			results[k] = v
			fmt.Println("Text:", k, "Embedding:", v)
		}
	}

	return results
}
