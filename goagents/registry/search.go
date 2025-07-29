package registry

import "context"

type SearchEngine struct {
	ES        *ESAgentRegistry
	Embedding *OpenAIEmbeddingStore
	Cache     *EmbeddingCache
}

func (s *SearchEngine) Search(
	ctx context.Context,
	query string,
	topK int,
) ([]*AgentCard, error) {

	return nil, nil
}
