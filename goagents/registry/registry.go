package registry

import (
	"bytes"
	"encoding/json"

	es "github.com/elastic/go-elasticsearch/v8"
)

type AgentCard struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Tags        []string `json:"tags"`
}

type AgentCardCreate struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Tags        []string  `json:"tags"`
	Vector      []float64 `json:"vector"`
}

type AgentRegistryI interface {
	Register(agent []*AgentCard) []string
	AreAgentsExists(ids []string) map[string]bool
}

type ESAgentRegistry struct {
	Client    *es.Client
	Indexname string
}

func NewESAgentRegistry(client *es.Client, indexname string) *ESAgentRegistry {
	return &ESAgentRegistry{
		Client:    client,
		Indexname: indexname,
	}
}

// 성공한 에이전트의 id들을 반환함.
func (r *ESAgentRegistry) Register(agents []*AgentCard) []string {

	ids := make([]string, len(agents))
	targetIDs := make([]string, 0, len(agents))
	successIDs := make([]string, 0, len(agents))

	for i, agent := range agents {
		ids[i] = agent.ID
	}
	existingIDs := r.AreAgentsExists(ids)
	for id, isExist := range existingIDs {
		if isExist {
			targetIDs = append(targetIDs, id)
		}
	}

	for _, agent := range agents {
		agentBytes, err := json.Marshal(agent)
		if err != nil {
			continue
		}
		_, err = r.Client.Index(
			r.Indexname,
			bytes.NewReader(agentBytes),
			r.Client.Index.WithDocumentID(agent.ID),
		)
		if err != nil {
			continue
		}
		successIDs = append(successIDs, agent.ID)

		break
	}
	return successIDs
}

// 존재하는 에이전트의 id는 true, 존재하지 않는 에이전트의 id는 false로 반환함.
func (r *ESAgentRegistry) AreAgentsExists(ids []string) map[string]bool {

	exists := make(map[string]bool)

	for _, id := range ids {
		resp, err := r.Client.Get(r.Indexname, id)
		if err != nil {
			exists[id] = false
			continue
		}
		if resp.IsError() {
			exists[id] = false
			continue
		}
		exists[id] = true
		defer resp.Body.Close()
	}
	return exists
}
