package apis

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/sdkim96/dashboard/registry"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/openai/openai-go"
	opt "github.com/openai/openai-go/option"
	utl "github.com/sdkim96/dashboard/utils"
	providers "github.com/sdkim96/dashboard/utils/providers"
)

type AgentRecommended struct {
	AgentID        string    `json:"agent_id"`
	AgentVersion   int       `json:"agent_version"`
	DepartmentName string    `json:"department_name"`
	Name           string    `json:"name"`
	Description    string    `json:"description"`
	Tags           []string  `json:"tags"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
}

func RecommendAgents(query string, userContext string) ([]*AgentRecommended, error) {
	err := utl.LoadEnv()
	if err != nil {
		return nil, fmt.Errorf("Error loading .env file: %s", err)
	}
	agentRecommended := make([]*AgentRecommended, 0)

	OpenAIClient := openai.NewClient(opt.WithAPIKey(os.Getenv("OPENAI_API_KEY")))
	ESClient, err := es.NewClient(
		es.Config{
			Addresses: []string{os.Getenv("ELASTICSEARCH_URL")},
			APIKey:    os.Getenv("ELASTICSEARCH_API_KEY"),
		},
	)
	if err != nil {
		return nil, fmt.Errorf("Error creating Elasticsearch client: %s", err)
	}
	embeddingStore := utl.NewOpenAIEmbeddingStore(&OpenAIClient)
	cache := utl.NewVectorCache()
	rg := registry.NewESRegistry(ESClient, "agents")
	ai := providers.NewOpenAIProvider(&OpenAIClient, "You are a helpful assistant that provides information about agents.")
	ctx := context.Background()

	engine := registry.Init(
		rg,
		embeddingStore,
		cache,
		ai,
	)
	cards, err := engine.Search(
		ctx,
		query,
		registry.WithUserContext(userContext),
	)
	if err != nil {
		return nil, fmt.Errorf("Error searching agents: %s", err)
	}
	if len(cards) == 0 {
		return nil, fmt.Errorf("Expected to find at least one agent, but found none")
	} else {
		for _, card := range cards {
			agentRecommended = append(agentRecommended, &AgentRecommended{
				AgentID:        card.ID,
				AgentVersion:   1,
				DepartmentName: card.DepartmentName,
				Name:           card.Name,
				Description:    card.Description,
				Tags:           card.Tags,
				CreatedAt:      time.Now(),
				UpdatedAt:      time.Now(),
			})
		}
	}

	return agentRecommended, nil
}
