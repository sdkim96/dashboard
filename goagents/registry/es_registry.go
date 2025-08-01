package registry

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	es "github.com/elastic/go-elasticsearch/v8"
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

type ESRegistry struct {
	Client    *es.Client
	Indexname string
}

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

func NewESRegistry(client *es.Client, indexname string) *ESRegistry {
	return &ESRegistry{
		Client:    client,
		Indexname: indexname,
	}
}

func (rg *ESRegistry) CreateIndex(
	ctx context.Context,
	definition string,
) error {
	resp, err := esapi.IndicesCreateRequest{
		Index: rg.Indexname,
		Body:  strings.NewReader(definition),
	}.Do(ctx, rg.Client)
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

func (rg *ESRegistry) InsertAgentCard(
	ctx context.Context,
	card *AgentCardCreate,
) error {
	marshaled, err := json.Marshal(card)
	if err != nil {
		return err
	}

	resp, err := esapi.IndexRequest{
		Index:      rg.Indexname,
		DocumentID: card.ID,
		Body:       bytes.NewReader(marshaled),
	}.Do(ctx, rg.Client)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.IsError() {
		return fmt.Errorf("error inserting agent card: %s", resp.String())
	}
	return nil
}

func (rg *ESRegistry) DeleteIndex(ctx context.Context) error {
	resp, err := esapi.IndicesDeleteRequest{
		Index: []string{rg.Indexname},
	}.Do(ctx, rg.Client)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.IsError() {
		return fmt.Errorf("error deleting index: %s", resp.String())
	}
	return nil
}

func (rg *ESRegistry) DeleteAgentCard(ctx context.Context, id string) error {
	resp, err := esapi.DeleteRequest{
		Index:      rg.Indexname,
		DocumentID: id,
	}.Do(ctx, rg.Client)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.IsError() {
		return fmt.Errorf("error deleting agent card: %s", resp.String())
	}
	return nil
}

func (rg *ESRegistry) GetAgentCard(ctx context.Context, id string) (*AgentCard, error) {
	resp, err := esapi.GetRequest{
		Index:      rg.Indexname,
		DocumentID: id,
	}.Do(ctx, rg.Client)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.IsError() {
		return nil, fmt.Errorf("error getting agent card: %s", resp.String())
	}

	var card AgentCard
	if err := json.NewDecoder(resp.Body).Decode(&card); err != nil {
		return nil, fmt.Errorf("error decoding response: %s", err)
	}
	return &card, nil
}

func (rg *ESRegistry) Search(
	ctx context.Context,
	query string,
) ([]*AgentCard, error) {
	resp, err := esapi.SearchRequest{
		Index: []string{rg.Indexname},
		Body:  strings.NewReader(query),
	}.Do(ctx, rg.Client)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.IsError() {
		return nil, fmt.Errorf("error searching agent cards: %s", resp.String())
	}

	var result struct {
		Hits struct {
			Hits []struct {
				Source AgentCard `json:"_source"`
			} `json:"hits"`
		} `json:"hits"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("error decoding search response: %s", err)
	}

	cards := make([]*AgentCard, len(result.Hits.Hits))
	for i, hit := range result.Hits.Hits {
		cards[i] = &hit.Source
	}
	return cards, nil
}
