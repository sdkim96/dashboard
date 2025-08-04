package registry

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"strings"
	"time"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/elastic/go-elasticsearch/v8/esapi"
)

const IndexDefinition = `{
	"settings": {
		"analysis": {
			"analyzer": {
				"korean_analyzer": {
					"type": "custom",
					"tokenizer": "nori_tokenizer",
					"filter": [
						"nori_readingform",
						"lowercase",
						"nori_stop_filter"
					]
				},
				"korean_search_analyzer": {
					"type": "custom",
					"tokenizer": "nori_tokenizer",
					"filter": [
						"nori_readingform",
						"lowercase",
						"nori_stop_filter"
					]
				}
			},
			"tokenizer": {
				"nori_tokenizer": {
					"type": "nori_tokenizer",
					"decompound_mode": "mixed"
				}
			},
			"filter": {
				"nori_stop_filter": {
					"type": "nori_part_of_speech",
					"stoptags": [
						"SP",
						"SSC",
						"SSO",
						"SC",
						"SE",
						"XPN",
						"XSA",
						"XSN",
						"XSV",
						"UNA",
						"NA",
						"VSV"
					]
				}
			}
		}
	},
	"mappings": {
		"properties": {
			"id": {"type": "keyword"},
			"agent_id": {"type": "keyword"},
			"agent_version": {"type": "integer"},
			"name": {
				"type": "text",
				"analyzer": "korean_analyzer",
				"search_analyzer": "korean_search_analyzer",
				"fields": {
					"keyword": {"type": "keyword"}
				}
			},
			"department_name": {
				"type": "keyword",
				"fields": {
					"korean": {
						"type": "text",
						"analyzer": "korean_analyzer"
					}
				}
			},
			"description": {
				"type": "text",
				"analyzer": "korean_analyzer",
				"search_analyzer": "korean_search_analyzer"
			},
			"description_vector": {
				"type": "dense_vector",
				"dims": 1536,
				"index": true,
				"similarity": "cosine"
			},
			"prompt": {
				"type": "text",
				"analyzer": "korean_analyzer",
				"search_analyzer": "korean_search_analyzer"
			},
			"prompt_vector": {
				"type": "dense_vector",
				"dims": 1536,
				"index": true,
				"similarity": "cosine"
			},
			"tags": {
				"type": "keyword",
				"fields": {
					"korean": {
						"type": "text",
						"analyzer": "korean_analyzer"
					}
				}
			},
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

// **Private function**
//
// isIndexExists checks if the index exists in Elasticsearch.
func (s *ESRegistry) isIndexExists(ctx context.Context) (bool, error) {
	resp, err := esapi.IndicesExistsRequest{
		Index: []string{s.Indexname},
	}.Do(ctx, s.Client)
	if err != nil {
		return false, fmt.Errorf("error checking if index exists: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode == 404 {
		return false, nil
	}
	if resp.IsError() {
		return false, fmt.Errorf("error checking if index exists: %s", resp.String())
	}
	if resp.StatusCode == 200 {
		return true, nil
	}

	return false, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
}

func NewESRegistry(client *es.Client, indexname string) *ESRegistry {
	return &ESRegistry{
		Client:    client,
		Indexname: indexname,
	}
}

func (rg *ESRegistry) CreateIndexIfNotExists(
	ctx context.Context,
	definition string,
) error {

	exists, err := rg.isIndexExists(ctx)
	if err != nil {
		return fmt.Errorf("error checking if index exists: %w", err)
	}
	if exists {
		return nil
	}

	resp, err := esapi.IndicesCreateRequest{
		Index: rg.Indexname,
		Body:  strings.NewReader(definition),
	}.Do(ctx, rg.Client)
	if err != nil {
		return fmt.Errorf("error creating index: %w", err)
	}
	defer resp.Body.Close()
	if resp.IsError() {
		return fmt.Errorf("error creating index: %s", resp.String())
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
	search *AgentCardHybridSearch,
	descriptionVector []float64,
	promptVector []float64,
) ([]*AgentCard, error) {

	query := map[string]interface{}{
		"size": search.TopK,
		"query": map[string]interface{}{
			"script_score": map[string]interface{}{
				"query": map[string]interface{}{
					"bool": map[string]interface{}{
						"should": []interface{}{
							map[string]interface{}{
								"match": map[string]interface{}{
									"description": map[string]interface{}{
										"query": search.QueryRewrited,
										"boost": search.Boost.QueryRewrited,
									},
								},
							},
							map[string]interface{}{
								"match": map[string]interface{}{
									"prompt": map[string]interface{}{
										"query": search.QueryRewrited,
										"boost": search.Boost.QueryRewrited,
									},
								},
							},
							map[string]interface{}{
								"terms": map[string]interface{}{
									"tags": search.Tags,
								},
							},
							map[string]interface{}{
								"exists": map[string]interface{}{
									"field": "description_vector",
								},
							},
						},
						"minimum_should_match": 1,
					},
				},
				"script": map[string]interface{}{
					"source": `
						double descScore = cosineSimilarity(params.descVector, 'description_vector') * params.descBoost;
						double promptScore = cosineSimilarity(params.promptVector, 'prompt_vector') * params.promptBoost;
						return descScore + promptScore + _score + 1.0;
					`,
					"params": map[string]interface{}{
						"descVector":   descriptionVector,
						"promptVector": promptVector,
						"descBoost":    search.Boost.QueryRewrited,
						"promptBoost":  search.Boost.QueryRewrited,
					},
				},
			},
		},
	}

	queryMarshaled, err := json.Marshal(query)
	if err != nil {
		return nil, fmt.Errorf("error marshaling query: %w", err)
	}
	body := bytes.NewReader(queryMarshaled)

	res, err := rg.Client.Search(
		rg.Client.Search.WithContext(ctx),
		rg.Client.Search.WithIndex(rg.Indexname),
		rg.Client.Search.WithBody(body),
	)
	if err != nil {
		return nil, fmt.Errorf("es search: %w", err)
	}
	defer res.Body.Close()

	if res.IsError() {
		return nil, fmt.Errorf("search error: %s", res.String())
	}

	var r struct {
		Hits struct {
			Hits []struct {
				Source *AgentCard `json:"_source"`
			} `json:"hits"`
		} `json:"hits"`
	}
	dataRead, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}
	json.Unmarshal(dataRead, &r)

	agentCards := make([]*AgentCard, 0, len(r.Hits.Hits))
	for _, hit := range r.Hits.Hits {
		agentCards = append(agentCards, hit.Source)
	}

	return agentCards, nil
}
