package providers

import (
	"context"

	"github.com/openai/openai-go"
	"github.com/openai/openai-go/shared"
)

type OpenAIChatOption func(*openai.ChatCompletionNewParams) *openai.ChatCompletionNewParams

type OpenAIProvider struct {
	Client       *openai.Client
	SystemPrompt string
}

func NewOpenAIProvider(client *openai.Client, SystemPrompt string) *OpenAIProvider {
	return &OpenAIProvider{
		Client:       client,
		SystemPrompt: SystemPrompt,
	}
}
func generateMessages(systemM string, userM string) []openai.ChatCompletionMessageParamUnion {
	return []openai.ChatCompletionMessageParamUnion{
		openai.SystemMessage(systemM),
		openai.UserMessage(userM),
	}
}
func (o *OpenAIProvider) Invoke(
	ctx context.Context,
	prompt string,
	deploymentID shared.ChatModel,
	opt ...OpenAIChatOption,
) (string, error) {
	params := &openai.ChatCompletionNewParams{
		Model:    deploymentID,
		Messages: generateMessages(o.SystemPrompt, prompt),
	}
	for _, o := range opt {
		params = o(params)
	}

	resp, err := o.Client.Chat.Completions.New(
		ctx,
		*params,
	)
	if err != nil {
		return "", err
	}
	if len(resp.Choices) == 0 {
		return "", nil
	}
	return resp.Choices[0].Message.Content, nil
}
