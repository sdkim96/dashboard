package registry

import (
	"os"
	"path/filepath"
	"testing"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/joho/godotenv"
)

func TestCreateIndex(t *testing.T) {

	currentDir, err := os.Getwd()
	if err != nil {
		t.Fatalf("Error getting current directory: %s", err)
	}
	projectDir := filepath.Join(currentDir, "..", "..")
	err = godotenv.Load(projectDir + "/.env")
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
	rg := NewESRegistry(ESClient, "agents")

}
