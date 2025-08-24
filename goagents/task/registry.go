package task

import "fmt"

type AgentHeader struct {
	ID             string   `json:"agent_id"`
	DepartmentName string   `json:"department_name"`
	Name           string   `json:"name"`
	Description    string   `json:"description"`
	Tags           []string `json:"tags"`
}
type AgentBody struct {
	SystemPrompt string
}

func (h *AgentHeader) Describe() string {
	return fmt.Sprintf("Agent %s (%s): %s \n===\n", h.Name, h.DepartmentName, h.Description)
}

type AgentCard struct {
	AgentHeader
	AgentBody
	fn func()
}
