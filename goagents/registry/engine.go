package registry

import (
	"context"
	"strconv"
	"time"

	openai "github.com/openai/openai-go"
	utl "github.com/sdkim96/dashboard/utils"
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
	Embedding *utl.EmbeddingStoreI
	Cache     *utl.EmbeddingCacheI
	AIClient  *AIClient
}

func Init(
	registry AgentRegistryI,
	embedding utl.EmbeddingStoreI,
	cache utl.EmbeddingCacheI,
	aiClient *AIClient,
) *SearchEngine {
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
	opt ...func(*AgentCardCreate) *AgentCardCreate,
) error {

	ID := agentID + "-" + strconv.Itoa(agentVersion)
	embedTarget := make([]string, 0, 2)

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

	embedding := *(s.Embedding)
	embedTarget = append(embedTarget, description)

	if agentCard.Prompt != "" {
		embedTarget = append(embedTarget, agentCard.Prompt)
	}
	embedded := embedding.EmbedBatch(embedTarget)

	descriptionEmbedding := embedded[agentCard.Description]
	promptEmbedding := embedded[agentCard.Prompt]

	agentCard.DescriptionVector = descriptionEmbedding
	agentCard.PromptVector = promptEmbedding

	err := (*s.Registry).InsertAgentCard(ctx, agentCard)
	if err != nil {
		return err
	}

	return nil
}

func WithAgentName(name string) func(*AgentCardCreate) *AgentCardCreate {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.Name = name
		return card
	}
}
func WithAgentTags(tags []string) func(*AgentCardCreate) *AgentCardCreate {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.Tags = tags
		return card
	}
}
func WithAgentDepartmentName(departmentName string) func(*AgentCardCreate) *AgentCardCreate {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.DepartmentName = departmentName
		return card
	}
}
func WithAgentPrompt(prompt string) func(*AgentCardCreate) *AgentCardCreate {
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
