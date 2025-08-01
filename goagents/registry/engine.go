package registry

import (
	"context"
	"strconv"
	"time"

	utl "github.com/sdkim96/dashboard/utils"
	providers "github.com/sdkim96/dashboard/utils/providers"
)

type RegisterAgentOption func(*AgentCardCreate) *AgentCardCreate
type HybridSearchAgentOption func(*AgentCardHybridSearch) *AgentCardHybridSearch

type SearchEngine struct {
	Registry  *AgentRegistryI
	Embedding *utl.EmbeddingStoreI
	Cache     *utl.EmbeddingCacheI
	AIClient  *providers.OpenAIClient
}
type Boost struct {
	Description float64 `json:"description"`
	Prompt      float64 `json:"prompt"`
	Tags        float64 `json:"tags"`
}
type AgentCardHybridSearch struct {
	QueryToDescription string   `json:"query"`
	QueryToPrompt      string   `json:"prompt"`
	Tags               []string `json:"tags"`
	TopK               int      `json:"top_k"`
	Boost              Boost    `json:"boost"`
}

func Init(
	registry AgentRegistryI,
	embedding utl.EmbeddingStoreI,
	cache utl.EmbeddingCacheI,
	aiClient *providers.OpenAIClient,
) *SearchEngine {

	err := registry.CreateIndexIfNotExists(
		context.Background(),
		IndexDefinition,
	)
	if err != nil {
		return nil
	}

	return &SearchEngine{
		Registry:  &registry,
		Embedding: &embedding,
		Cache:     &cache,
		AIClient:  aiClient,
	}
}

func (s *SearchEngine) RegisterAgent(
	ctx context.Context,
	agentID string,
	agentVersion int,
	description string,
	opt ...RegisterAgentOption,
) error {

	var (
		ID              string
		embedTargets    []string
		openAIVectorMap map[string][]float64
	)

	ID = agentID + "-" + strconv.Itoa(agentVersion)
	embedTargets = make([]string, 0, 2)
	openAIEmbeddingStore := *(s.Embedding)

	agentCard := &AgentCardCreate{
		ID:           ID,
		AgentID:      agentID,
		AgentVersion: agentVersion,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}
	for _, o := range opt {
		o(agentCard)
	}

	embedTargets = append(embedTargets, description)
	if agentCard.Prompt != "" {
		embedTargets = append(embedTargets, agentCard.Prompt)
	}

	openAIVectorMap = openAIEmbeddingStore.EmbedBatch(embedTargets)

	descriptionVector := openAIVectorMap[agentCard.Description]
	promptVector := openAIVectorMap[agentCard.Prompt]

	agentCard.DescriptionVector = descriptionVector
	agentCard.PromptVector = promptVector

	err := (*s.Registry).InsertAgentCard(ctx, agentCard)
	if err != nil {
		return err
	}

	return nil
}

func WithAgentName(name string) RegisterAgentOption {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.Name = name
		return card
	}
}
func WithAgentTags(tags []string) RegisterAgentOption {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.Tags = tags
		return card
	}
}
func WithAgentDepartmentName(departmentName string) RegisterAgentOption {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.DepartmentName = departmentName
		return card
	}
}
func WithAgentPrompt(prompt string) RegisterAgentOption {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.Prompt = prompt
		return card
	}
}

func (s *SearchEngine) Search(
	ctx context.Context,
	query string,
	topK int,
) ([]*AgentCard, error) {

	return nil, nil
}
