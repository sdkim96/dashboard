package registry

import (
	"context"

	openai "github.com/openai/openai-go"
)

type AIClient struct {
	Client       *openai.Client
	SystemPrompt string
}

func NewAIClient(client *openai.Client, SystemPrompt string) *AIClient {
	return &AIClient{
		Client:       client,
		SystemPrompt: SystemPrompt,
	}
}

type SearchEngine struct {
	Registry  *AgentRegistryI
	Embedding *EmbeddingStoreI
	Cache     *EmbeddingCacheI
	AIClient  *AIClient
}

func Init(
	registry AgentRegistryI,
	embedding EmbeddingStoreI,
	cache EmbeddingCacheI,
	aiClient *AIClient,
) *SearchEngine {
	return &SearchEngine{
		Registry:  &registry,
		Embedding: &embedding,
		Cache:     &cache,
		AIClient:  aiClient,
	}
}

func (s *SearchEngine) Search(
	ctx context.Context,
	query string,
	topK int,
) ([]*AgentCard, error) {

	return nil, nil
}
