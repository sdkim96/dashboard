package providers

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/openai/openai-go"
	"github.com/openai/openai-go/shared"

	utl "github.com/sdkim96/dashboard/utils"
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
func InvokeStructuredOutput[T any](
	ctx context.Context,
	p *OpenAIProvider,
	prompt string,
	deploymentID shared.ChatModel,
) (T, error) {
	var zero T

	if deploymentID == "" {
		return zero, fmt.Errorf("model(deploymentID) is required")
	}
	schema := utl.GenerateSchema[T]()

	params := openai.ChatCompletionNewParams{
		Model:    deploymentID,
		Messages: generateMessages(p.SystemPrompt, prompt),
	}

	params.ResponseFormat = openai.ChatCompletionNewParamsResponseFormatUnion{
		OfJSONSchema: &openai.ResponseFormatJSONSchemaParam{
			JSONSchema: openai.ResponseFormatJSONSchemaJSONSchemaParam{
				Name:        "Schema",
				Description: openai.String("Response Schema"),
				Schema:      schema,
				Strict:      openai.Bool(true),
			},
		},
	}

	chat, err := p.Client.Chat.Completions.New(ctx, params)
	if err != nil {
		return zero, fmt.Errorf("chat completion failed: %w", err)
	}

	if chat == nil || len(chat.Choices) == 0 {
		return zero, fmt.Errorf("empty response from OpenAI")
	}
	content := chat.Choices[0].Message.Content
	if content == "" {
		return zero, fmt.Errorf("empty message content")
	}

	var out T
	if err := json.Unmarshal([]byte(content), &out); err != nil {
		return zero, fmt.Errorf("unmarshal to %T failed: %w; raw=%s", out, err, content)
	}
	return out, nil
}
