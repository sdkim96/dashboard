package registry

import (
	"context"
	"os"
	"path/filepath"
	"testing"
	"time"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/joho/godotenv"
)

const TestIndexName = "test_agents"

func loadEnv() error {
	currentDir, err := os.Getwd()
	if err != nil {
		return err
	}
	projectDir := filepath.Join(currentDir, "..", "..")
	return godotenv.Load(projectDir + "/.env")
}

func TestCreateIndexIfNotExists(t *testing.T) {

	err := loadEnv()

	ESClient, err := es.NewClient(
		es.Config{
			Addresses: []string{os.Getenv("ELASTICSEARCH_URL")},
			APIKey:    os.Getenv("ELASTICSEARCH_API_KEY"),
		},
	)
	if err != nil {
		t.Fatalf("Error creating Elasticsearch client: %s", err)
	}
	rg := NewESRegistry(ESClient, TestIndexName)
	err = rg.CreateIndexIfNotExists(
		context.Background(),
		IndexDefinition,
	)
	if err != nil {
		t.Fatalf("Error creating index: %s", err)
	}
	err = rg.DeleteIndex(context.Background())
	if err != nil {
		t.Fatalf("Error deleting index: %s", err)
	}

}

func TestInsertAgentCard(t *testing.T) {

	err := loadEnv()
	if err != nil {
		t.Fatalf("Error loading .env file: %s", err)
	}

	ESClient, err := es.NewClient(
		es.Config{
			Addresses: []string{os.Getenv("ELASTICSEARCH_URL")},
			APIKey:    os.Getenv("ELASTICSEARCH_API_KEY"),
		},
	)
	if err != nil {
		t.Fatalf("Error creating Elasticsearch client: %s", err)
	}
	rg := NewESRegistry(ESClient, TestIndexName)
	err = rg.CreateIndexIfNotExists(
		context.Background(),
		IndexDefinition,
	)
	if err != nil {
		t.Fatalf("Error creating index: %s", err)
	}

	descriptionVector := make([]float64, 1536)
	promptVector := make([]float64, 1536)

	for i := 0; i < 1536; i++ {

		descriptionVector[i] = float64(i) / 1000.0
		promptVector[i] = float64(i) / 2000.0
	}

	card := &AgentCardCreate{
		ID:                "test-agent-1",
		AgentID:           "test-agent",
		AgentVersion:      1,
		Name:              "Test Agent",
		DepartmentName:    "Test Department",
		Description:       "This is a test agent.",
		DescriptionVector: descriptionVector,
		Prompt:            "This is a test prompt.",
		PromptVector:      promptVector,
		Tags:              []string{"test", "agent"},
		CreatedAt:         time.Now(),
		UpdatedAt:         time.Now(),
	}

	err = rg.InsertAgentCard(context.Background(), card)
	if err != nil {
		t.Fatalf("Error inserting agent card: %s", err)
	}

}
