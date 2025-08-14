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
	"github.com/sdkim96/dashboard/registry"
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
type StepBody struct {
	AgentID     string `json:"agent_id"`
	Query       string `json:"query"`
	MinimumGoal string `json:"minimum_goal"`
}
type Step struct {
	ID            string    `json:"id"`
	PlanID        string    `json:"plan_id"`
	AgentID       string    `json:"agent_id"`
	BeforeAgentID string    `json:"before_id"`
	CreatedAt     time.Time `json:"created_at"`
	StepBody      StepBody  `json:"step_body"`
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

var NewStepPrompt = `
## 역할
당신은 좋은 목표 수립기입니다.

## 목표
- 사용자의 질문과 <목표>를 바탕으로. 유저가 달성하기 위해 필요한 **단계**를 수립합니다.
- <에이전트 풀>에 있는 에이전트들을 활용하여, 유저가 목표를 달성하기 위해 필요한 <단계>를 수립하시오.

## <단계>
- 단계는 유저가 목표를 달성하기 위해 **필요한 에이전트**와 그 **에이전트에 질문해야할 질문**과 달성해야하는 **최소 목표 설명**를 포함해야 합니다.

## <에이전트 풀>
%s 

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

func (p *Planner) PlanStep(
	ctx context.Context,
	agents []*registry.AgentCard,
) (string, error) {
	uid4 := "step-" + uuid.New().String()
	systemPrompt := fmt.Sprintf(
		NewStepPrompt,
		agents,
		p.Plan.Context,
	)
	openaiClient := openai.NewClient(opt.WithAPIKey(os.Getenv("OPENAI_API_KEY")))
	ai := providers.NewOpenAIProvider(&openaiClient, systemPrompt)

	stepBody, err := providers.InvokeStructuredOutput[StepBody](
		ctx,
		ai,
		"작업 스텝을 만들어줘",
		shared.ChatModelGPT4oMini,
	)
	if err != nil {
		fmt.Printf("Error invoking OpenAI for step planning: %s\n", err)
		return uid4, err
	}
	step := &Step{
		ID:            uid4,
		PlanID:        p.Plan.ID,
		AgentID:       stepBody.AgentID,
		BeforeAgentID: RootAgentID,
		CreatedAt:     time.Now(),
		StepBody:      stepBody,
		Result:        "",
	}
	p.Steps[step.ID] = step
	return uid4, nil
}

func (p *Planner) FinishStep(
	stepID string,
	result string,
) {
	if step, exists := p.Steps[stepID]; exists {
		step.Result = result
		fmt.Printf("Step %s finished with result: %s\n", step.ID, step.Result)
	}
	p.Plan.SetFinalStepID(stepID)
	fmt.Printf("Step with ID %s not found\n", stepID)
}

func (p *Planner) DecideCompletion(stepID string, result string) {}
