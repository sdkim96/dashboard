package apis

import (
	"context"
	"fmt"
	"os"

	"github.com/sdkim96/dashboard/registry"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/openai/openai-go"
	opt "github.com/openai/openai-go/option"
	utl "github.com/sdkim96/dashboard/utils"
	providers "github.com/sdkim96/dashboard/utils/providers"
)

func RecommendAgents(query string, userContext string) ([]*registry.AgentCard, error) {
	err := utl.LoadEnv()
	if err != nil {
		return nil, fmt.Errorf("Error loading .env file: %s", err)
	}

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
			fmt.Printf("Found agent: %s - %s\n", card.ID, card.Description)
		}
	}

	return cards, nil
}
