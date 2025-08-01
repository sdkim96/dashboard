package utils_test

import (
	"fmt"
	"os"
	"strconv"
	"testing"

	openai "github.com/openai/openai-go"
	opt "github.com/openai/openai-go/option"
	utl "github.com/sdkim96/dashboard/utils"
	"github.com/stretchr/testify/assert"
)

func TestEmbed(t *testing.T) {
	Client := openai.NewClient(opt.WithAPIKey(os.Getenv("SDKIM_OPENAI_API_KEY")))
	store := utl.NewOpenAIEmbeddingStore(&Client)
	texts := make([]string, 0, 2)
	for i := 0; i < 10; i++ {
		text := "This is a test text for embedding " + strconv.Itoa(i)
		texts = append(texts, text)
	}
	successMap := store.EmbedBatch(texts)

	fmt.Println("Embedding results:")
	for j, res := range successMap {
		fmt.Printf("Text: %s\nEmbedding: %v\n", j, res)
	}

	assert.NotNil(t, successMap)
	assert.Len(t, successMap, 10)
}
