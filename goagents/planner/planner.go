package planner

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/google/uuid"
	"github.com/openai/openai-go"
	opt "github.com/openai/openai-go/option"
	"github.com/openai/openai-go/shared"
	"github.com/sdkim96/dashboard/utils/providers"
)

const RootStepID = "root"
const RootAgentID = "root-agent"

// Plan
//
// Plan represents a plan for an task(user's query)
type Plan struct {
	ID           string    `json:"id"`
	Objective    string    `json:"objective"`
	Context      string    `json:"context"`
	MaximumSteps int       `json:"maximum_steps"`
	IsCompleted  bool      `json:"is_completed"`
	CreatedAt    time.Time `json:"created_at"`
	FinalStepID  string    `json:"final_step_id"`
}

func (p *Plan) IsFinished() bool {
	return p.IsCompleted
}
func (p *Plan) SetFinalStepID(stepID string) {
	p.FinalStepID = stepID
	fmt.Printf("Final step ID set to: %s\n", p.FinalStepID)
}

// Step
//
// Step represents a step in the plan.
// Each step is associated with an agent that will execute the step.
type Step struct {
	ID            string    `json:"id"`
	PlanID        string    `json:"plan_id"`
	AgentID       string    `json:"agent_id"`
	BeforeAgentID string    `json:"before_id"`
	CreatedAt     time.Time `json:"created_at"`
	Query         string    `json:"query"`
	Result        string    `json:"result"`
}

func (s *Step) IsFinished() bool {
	return s.Result != ""
}

// 에이전트 플랜을 세우고 플랜을 관리하는 ControlPlane
// 플랜을 세우면, 세운 플랜을 router에게 전달한다.
type Planner struct {
	Plan  *Plan
	Steps map[string]*Step
}

var NewPlanPrompt = `
## 역할
당신은 좋은 목표 수립기입니다.

## 목표
- 사용자의 질문과 <문맥>을 바탕으로 유저가 달성하고자 하는 **목표**를 수립합니다.
- **목표**는 명확하고 구체적이어야 하며, 사용자가 달성하고자 하는 바를 명확히 해야 합니다.
- 결과는 20-30자 이내로 작성합니다.

## 설명
- <문맥>: 사용자의 지난 대화 내용이나 유저가 처한 상황입니다.

## <문맥>
%s
`

func NewPlanner(
	ctx context.Context,
	query string,
	userContext string,
	maximumSteps int,
) *Planner {

	uid4 := "plan-" + uuid.New().String()
	openaiClient := openai.NewClient(opt.WithAPIKey(os.Getenv("OPENAI_API_KEY")))

	plan := &Plan{
		ID:           uid4,
		Objective:    query,
		Context:      userContext,
		MaximumSteps: maximumSteps,
		IsCompleted:  false,
		CreatedAt:    time.Now(),
		FinalStepID:  RootStepID,
	}

	planner := &Planner{
		Plan:  plan,
		Steps: make(map[string]*Step),
	}

	systemPrompt := fmt.Sprintf(NewPlanPrompt, userContext)
	ai := providers.NewOpenAIProvider(&openaiClient, systemPrompt)
	objective, err := ai.Invoke(
		ctx,
		query,
		shared.ChatModelGPT4oMini,
	)
	if err != nil {
		fmt.Printf("Error invoking OpenAI: %s\n", err)
		return planner
	}
	plan.Objective = objective
	fmt.Printf("Plan created with ID: %s, Objective: %s\n", plan.ID, plan.Objective)
	return planner
}

// Returns the current Step ID
func (p *Planner) AddStep(
	agentID string,
	beforeAgentID string,
	query string,
) string {
	uid4 := "step-" + uuid.New().String()
	step := &Step{
		ID:            uid4,
		PlanID:        p.Plan.ID,
		AgentID:       agentID,
		BeforeAgentID: beforeAgentID,
		CreatedAt:     time.Now(),
		Query:         query,
		Result:        "",
	}
	p.Steps[uid4] = step
	fmt.Printf("Step added with ID: %s, Query: %s\n", step.ID, step.Query)
	return uid4
}

func (p *Planner) FinishStep(stepID string, result string) {
	if step, exists := p.Steps[stepID]; exists {
		step.Result = result
		fmt.Printf("Step %s finished with result: %s\n", step.ID, step.Result)
	}
	p.Plan.SetFinalStepID(stepID)
	fmt.Printf("Step with ID %s not found\n", stepID)
}

func (p *Planner) DecideCompletion(stepID string, result string) {}
