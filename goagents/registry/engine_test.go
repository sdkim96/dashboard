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
	utl "github.com/sdkim96/dashboard/utils"
	providers "github.com/sdkim96/dashboard/utils/providers"

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

	embeddingStore := utl.NewOpenAIEmbeddingStore(&OpenAIClient)
	cache := utl.NewVectorCache()
	rg := registry.NewESRegistry(ESClient, "agents")
	ai := providers.NewOpenAIClient(&OpenAIClient, "You are a helpful assistant that provides information about agents.")
	ctx := context.Background()

	// Initialize the search engine
	searchEngine := registry.Init(
		rg,
		embeddingStore,
		cache,
		ai,
	)
	errChan := make(chan error, 1)

	go func() {
		defer close(errChan)
		errChan <- searchEngine.RegisterAgent(
			ctx,
			"agent-123",
			1,
			"This is a test agent description.",
			registry.WithAgentName("Test Agent"),
			registry.WithAgentDepartmentName("Engineering"),
			registry.WithAgentPrompt("What can you do?"),
			registry.WithAgentTags([]string{"test", "agent"}),
		)
	}()

	go func() {
		err = <-errChan
	}()
	if err != nil {
		t.Fatalf("Error registering agent: %s", err)
	}
	searchEngine.Search(
		context.Background(),
		"test query",
		5,
	)

	if searchEngine == nil {
		t.Error("Expected search engine to be initialized, but it was nil")
	}
}

const TestIndexName = "test_agents"

func loadEnv() error {
	currentDir, err := os.Getwd()
	if err != nil {
		return err
	}
	projectDir := filepath.Join(currentDir, "..", "..")
	return godotenv.Load(projectDir + "/.env")
}

func TestBatch(t *testing.T) {
	err := loadEnv()
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
	embeddingStore := utl.NewOpenAIEmbeddingStore(&OpenAIClient)
	cache := utl.NewVectorCache()
	rg := registry.NewESRegistry(ESClient, "agents")
	ai := providers.NewOpenAIClient(&OpenAIClient, "You are a helpful assistant that provides information about agents.")
	ctx := context.Background()

	// Initialize the search engine
	engine := registry.Init(
		rg,
		embeddingStore,
		cache,
		ai,
	)

	go func() {

	}()
	engine.RegisterAgent(
		ctx,
		"agent-123",
		1,
		"This is a test agent description.",
		registry.WithAgentName("Test Agent"),
		registry.WithAgentDepartmentName("Engineering"),
		registry.WithAgentPrompt("What can you do?"),
		registry.WithAgentTags([]string{"test", "agent"}),
	)

}
