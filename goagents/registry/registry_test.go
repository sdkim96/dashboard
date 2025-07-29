package registry_test

import (
	"fmt"
	"strconv"
	"sync"
	"testing"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/sdkim96/dashboard/registry"
)

func TestRegister(t *testing.T) {
	var wg sync.WaitGroup
	wg.Add(10)
	client, err := es.NewDefaultClient()
	if err != nil {
		t.Fatalf("Error creating Elasticsearch client: %s", err)
	}
	rg := &registry.ESAgentRegistry{
		Client:    client,
		Indexname: "agents",
	}
	go func() {
		for i := 0; i < 10; i++ {
			agent := &registry.AgentCard{
				ID:          "agent" + strconv.Itoa(i),
				Name:        "Test Agent " + strconv.Itoa(i),
				Description: "This is a test agent " + strconv.Itoa(i),
				Tags:        []string{"test", "agent"},
			}
			rg.Register([]*registry.AgentCard{agent})
			fmt.Printf("Registered agent: %s\n", agent.ID)
			wg.Done()
		}
	}()
	wg.Wait()
}
