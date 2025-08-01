package providers

import (
	"github.com/openai/openai-go"
)

type OpenAIClient struct {
	Client       *openai.Client
	SystemPrompt string
}

func NewOpenAIClient(client *openai.Client, SystemPrompt string) *OpenAIClient {
	return &OpenAIClient{
		Client:       client,
		SystemPrompt: SystemPrompt,
	}
}
