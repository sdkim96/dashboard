package registry

import (
	"context"
)

type AgentCard struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Tags        []string `json:"tags"`
}

type AgentRegistryI interface {
	CreateIndexIfNotExists(ctx context.Context, definition string) error
	InsertAgentCard(ctx context.Context, card *AgentCardCreate) error
	DeleteIndex(ctx context.Context) error
	DeleteAgentCard(ctx context.Context, id string) error
	GetAgentCard(ctx context.Context, id string) (*AgentCard, error)
	Search(ctx context.Context, search *AgentCardHybridSearch, descriptionVector []float64, promptVector []float64) ([]*AgentCard, error)
}
