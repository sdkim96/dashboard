package registry_test

import (
	"context"
	"os"
	"path/filepath"
	"testing"

	"github.com/sdkim96/dashboard/registry"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/openai/openai-go"
	opt "github.com/openai/openai-go/option"

	"github.com/joho/godotenv"
)

func TestInit(t *testing.T) {
	currentDir, err := os.Getwd()
	if err != nil {
		t.Fatalf("Error getting current directory: %s", err)
	}
	projectDir := filepath.Join(currentDir, "..", "..")
	err = godotenv.Load(projectDir + "/.env")
	if err != nil {
		t.Fatalf("Error loading .env file: %s", err)
	}

	OpenAIClient := openai.NewClient(opt.WithAPIKey(os.Getenv("OPENAI_API_KEY")))
	ESClient, err := es.NewClient(
		es.Config{
			Addresses: []string{os.Getenv("ELASTICSEARCH_URL")},
			APIKey:    os.Getenv("ELASTICSEARCH_API_KEY"),
		},
	)
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
