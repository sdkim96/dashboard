package registry_test

import (
	"context"
	"os"
	"testing"

	"github.com/sdkim96/dashboard/registry"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/openai/openai-go"
	opt "github.com/openai/openai-go/option"
)

func TestInit(t *testing.T) {

	OpenAIClient := openai.NewClient(opt.WithAPIKey(os.Getenv("SDKIM_OPENAI_API_KEY")))
	ESClient, err := es.NewDefaultClient()
	if err != nil {
		t.Fatalf("Error creating Elasticsearch client: %s", err)
	}

	embeddingStore := registry.NewOpenAIEmbeddingStore(&OpenAIClient)
	cache := registry.NewVectorCache()
	rg := registry.NewESAgentRegistry(ESClient, "agents")
	ai := registry.NewAIClient(&OpenAIClient, "You are a helpful assistant that provides information about agents.")

	// Initialize the search engine
	searchEngine := registry.Init(
		rg,
		embeddingStore,
		cache,
		ai,
	)
	searchEngine.Search(
		context.Background(),
		"test query",
		5,
	)

	if searchEngine == nil {
		t.Error("Expected search engine to be initialized, but it was nil")
	}
}
