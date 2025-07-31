package registry

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/elastic/go-elasticsearch/v8/esapi"
)

const IndexDefinition = `{
	"mappings": {
		"properties": {
			"id": {"type": "keyword"},
			"agent_id": {"type": "keyword"},
			"agent_version": {"type": "integer"},
			"name": {
				"type": "text",
				"fields": {
					"keyword": {"type": "keyword"}
				}
			},
			"department_name": {"type": "keyword"},
			"description": {"type": "text"},
			"description_vector": {
				"type": "dense_vector",
				"dims": 1536,
				"index": true,
				"similarity": "cosine"
			},
			"prompt": {"type": "text"},
			"prompt_vector": {
				"type": "dense_vector",
				"dims": 1536,
				"index": true,
				"similarity": "cosine"
			},
			"tags": {"type": "keyword"},
			"created_at": {"type": "date"},
			"updated_at": {"type": "date"}
		}
	}
}`

type AgentCardCreate struct {
	ID                string    `json:"id"`
	AgentID           string    `json:"agent_id"`
	AgentVersion      int       `json:"agent_version"`
	Name              string    `json:"name"`
	DepartmentName    string    `json:"department_name"`
	Description       string    `json:"description"`
	DescriptionVector []float64 `json:"description_vector"`
	Prompt            string    `json:"prompt"`
	PromptVector      []float64 `json:"prompt_vector"`
	Tags              []string  `json:"tags"`
	CreatedAt         time.Time `json:"created_at"`
	UpdatedAt         time.Time `json:"updated_at"`
}

func CreateIndex(rg *ESAgentRegistry) error {
	resp, err := esapi.IndicesCreateRequest{
		Index: rg.Indexname,
		Body:  strings.NewReader(IndexDefinition),
	}.Do(context.Background(), rg.Client)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.IsError() {
		return fmt.Errorf("error creating index: %s", resp.String())
	}
	if resp.StatusCode != 200 && resp.StatusCode != 201 {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	if resp.StatusCode == 200 {
		fmt.Println("Index created successfully")
	}

	return nil
}
