package migration

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"os"
	"sync"

	"github.com/lib/pq"
	_ "github.com/lib/pq"

	es "github.com/elastic/go-elasticsearch/v8"
	"github.com/openai/openai-go"
	opt "github.com/openai/openai-go/option"

	rg "github.com/sdkim96/dashboard/registry"
	utl "github.com/sdkim96/dashboard/utils"
	providers "github.com/sdkim96/dashboard/utils/providers"
)

type AgentData struct {
	AgentID        string   `json:"agent_id"`
	AgentVersion   int      `json:"agent_version"`
	Name           string   `json:"name"`
	DepartmentName string   `json:"department_name"`
	Description    string   `json:"description"`
	Prompt         string   `json:"prompt"`
	Tags           []string `json:"tags"`
}

func getDataFromDB(limit int) []AgentData {
	utl.LoadEnv()
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s",
		os.Getenv("POSTGRES_HOST"),
		os.Getenv("POSTGRES_PORT"),
		os.Getenv("POSTGRES_USERNAME"),
		os.Getenv("POSTGRES_PASSWORD"),
		os.Getenv("POSTGRES_DB"),
	)
	agentDataList := make([]AgentData, 0)
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	sql := `
	select master.agent_id
     , detail.version as agent_version
     , master.name
     , master.department_name
     , detail.prompt
     , detail.description
     , array_agg(tag.tag) as tags
  from agent master
  join agent_detail detail
    on master.agent_id = detail.agent_id
  left join agent_tag tag
    on master.agent_id = tag.agent_id
  group by master.agent_id
         , detail.version
         , master.name
         , master.department_name
         , detail.prompt
         , detail.description
  limit $1
	`
	rows, err := db.Query(sql, limit)
	rowCount := 0
	for rows.Next() {
		var agentData AgentData
		var tags []string

		err = rows.Scan(&agentData.AgentID, &agentData.AgentVersion, &agentData.Name, &agentData.DepartmentName, &agentData.Prompt, &agentData.Description, pq.Array(&tags))
		if err != nil {
			log.Fatal(err)
		}

		agentData.Tags = tags

		fmt.Printf("Agent Data: %+s\n", agentData.Name)
		agentDataList = append(agentDataList, agentData)
		rowCount++
	}
	fmt.Printf("Total rows: %d\n", rowCount)
	return agentDataList
}

func initializeEngine() *rg.SearchEngine {
	OpenAIClient := openai.NewClient(opt.WithAPIKey(os.Getenv("OPENAI_API_KEY")))
	ESClient, err := es.NewClient(
		es.Config{
			Addresses: []string{os.Getenv("ELASTICSEARCH_URL")},
			APIKey:    os.Getenv("ELASTICSEARCH_API_KEY"),
		},
	)
	if err != nil {
		log.Fatalf("Error creating Elasticsearch client: %s", err)
	}

	embeddingStore := utl.NewOpenAIEmbeddingStore(&OpenAIClient)
	cache := utl.NewVectorCache()
	registry := rg.NewESRegistry(ESClient, "agents")
	ai := providers.NewOpenAIProvider(&OpenAIClient, "You are a helpful assistant that provides information about agents.")

	engine := rg.Init(registry, embeddingStore, cache, ai)
	return engine

}

func Migrate(agentDataList []AgentData, engine *rg.SearchEngine) {

	ctx := context.Background()

	sem := make(chan struct{}, 10)

	wg := sync.WaitGroup{}
	errChan := make(chan error, len(agentDataList))

	for _, agentData := range agentDataList {
		wg.Add(1)
		go func(agentData AgentData) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			log.Printf("Registering agent: %s", agentData.Name)

			err := engine.RegisterAgent(
				ctx,
				agentData.AgentID,
				agentData.AgentVersion,
				agentData.Description,
				rg.WithAgentName(agentData.Name),
				rg.WithAgentDepartmentName(agentData.DepartmentName),
				rg.WithAgentPrompt(agentData.Prompt),
				rg.WithAgentTags(agentData.Tags),
			)
			log.Printf("Finished registering agent: %s", agentData.Name)
			if err != nil {
				errChan <- err
			}
		}(agentData)
	}

	wg.Wait()
	close(errChan)

	var errs []error
	for err := range errChan {
		errs = append(errs, err)
		log.Printf("Error registering agent: %v", err)
	}

	// 에러가 있었다면 반환
	if len(errs) > 0 {
		log.Printf("Encountered %d errors during migration", len(errs))
	}

}
