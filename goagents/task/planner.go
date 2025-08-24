package task

import (
	"context"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/openai/openai-go"
	opt "github.com/openai/openai-go/option"
	"github.com/openai/openai-go/shared"
	"github.com/sdkim96/dashboard/utils/providers"
)

const RootAgentID = "root-agent"

// Plan
//
// Plan represents a plan for an task(user's query)
type Plan struct {
	id           string
	objective    string
	context      string
	maximumSteps int
	isCompleted  bool
}

func (p *Plan) ID() string {
	return p.id
}
func (p *Plan) Objective() string {
	return p.objective
}
func (p *Plan) MaximumSteps() int {
	return p.maximumSteps
}
func (p *Plan) Context() string {
	return p.context
}

func NewPlan(
	objective string,
	context string,
) (*Plan, error) {
	uid4 := "plan-" + uuid.New().String()
	plan := &Plan{
		id:           uid4,
		objective:    objective,
		context:      context,
		maximumSteps: 5,
		isCompleted:  false,
	}
	return plan, nil
}

func (p *Plan) Complete() {
	p.isCompleted = true
}
func (p *Plan) IsFinished() bool {
	return p.isCompleted
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
	id string
	StepBody
	result        string
	beforeAgentID string
	createdAt     time.Time
}

func (s *Step) ID() string {
	return s.id
}
func (s *Step) Result() string {
	return s.result
}

func NewStep(
	agentID string,
	query string,
	minimumGoal string,
	beforeAgentID string,
) (*Step, error) {
	uid4 := "step-" + uuid.New().String()
	step := &Step{
		id: uid4,
		StepBody: StepBody{
			AgentID:     agentID,
			Query:       query,
			MinimumGoal: minimumGoal,
		},
		result:        "",
		beforeAgentID: beforeAgentID,
		createdAt:     time.Now(),
	}
	return step, nil
}

func (s *Step) IsFinished() bool {
	return s.result != ""
}
func (s *Step) Complete(result string) {
	s.result = result
}

// 에이전트 플랜을 세우고 플랜을 관리하는 ControlPlane
// 플랜을 세우면, 세운 플랜을 router에게 전달한다.
type Planner struct {
	Plan  *Plan
	Steps map[string]*Step
	mu    sync.RWMutex
	ai    openai.Client
}

func (p *Planner) DescribeMe() string {
	var descriptions []string
	for _, step := range p.Steps {
		descriptions = append(descriptions, fmt.Sprintf("단계: %s, 결과: %s", step.Query, step.result))
	}
	return strings.Join(descriptions, "\n")
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

var IsPlanFinishedPrompt = `
## 역할
당신은 목표 달성 여부를 판단하는 AI입니다.

## 목표
- 주어진 계획이 완료되었는지 여부를 판단합니다.
- 각 <단계>의 결과를 바탕으로 <계획의 최종목표 달성> 여부를 결정합니다.
- 종료되었다고 판단하면 true, 그렇지 않으면 false를 반환합니다.

## <단계>
%s

## <계획의 최종목표>
%s
`

type IsFinished struct {
	Finished bool `json:"finished"`
}

func NewPlanner(
	ctx context.Context,
	query string,
	userContext string,
	maximumSteps int,
) (*Planner, error) {

	openaiClient := openai.NewClient(opt.WithAPIKey(os.Getenv("OPENAI_API_KEY")))
	systemPrompt := fmt.Sprintf(NewPlanPrompt, userContext)
	ai := providers.NewOpenAIProvider(&openaiClient, systemPrompt)
	objective, err := ai.Invoke(
		ctx,
		query,
		shared.ChatModelGPT4oMini,
	)
	if err != nil {
		fmt.Printf("Error invoking OpenAI: %s\n", err)
		return nil, err
	}

	plan, err := NewPlan(objective, userContext)
	if err != nil {
		fmt.Printf("Error creating new plan: %s\n", err)
		return nil, err
	}
	planner := &Planner{
		Plan:  plan,
		Steps: make(map[string]*Step),
		ai:    openaiClient,
		mu:    sync.RWMutex{},
	}

	return planner, nil
}

func (p *Planner) PlanStep(
	ctx context.Context,
	agents []*AgentHeader,
	beforeAgentID string,
) (*Step, error) {

	describes := make([]string, 0)
	for _, a := range agents {
		describes = append(describes, a.Describe())
	}

	systemPrompt := fmt.Sprintf(
		NewStepPrompt,
		describes,
		p.Plan.Context(),
	)
	ai := providers.NewOpenAIProvider(&p.ai, systemPrompt)

	stepBody, err := providers.InvokeStructuredOutput[StepBody](
		ctx,
		ai,
		"작업 스텝을 만들어줘",
		shared.ChatModelGPT4oMini,
	)
	if err != nil {
		fmt.Printf("Error invoking OpenAI for step planning: %s\n", err)
		return nil, err
	}
	newStep, err := NewStep(
		stepBody.AgentID,
		stepBody.Query,
		stepBody.MinimumGoal,
		beforeAgentID,
	)
	if err != nil {
		return nil, err
	}
	return newStep, nil
}

func (p *Planner) AddStep(step *Step) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	if _, exists := p.Steps[step.ID()]; exists {
		return fmt.Errorf("step %s already exists", step.ID())
	}
	p.Steps[step.ID()] = step
	return nil
}

func (p *Planner) CompleteStep(
	ctx context.Context,
	stepID string,
	result string,
) error {
	if step, exists := p.Steps[stepID]; exists {
		step.Complete(result)
		fmt.Printf("Step %s finished with result: %s\n", step.ID(), step.Result())
		return nil
	}
	return fmt.Errorf("step %s not found", stepID)
}

func (p *Planner) CheckPlanCompletion(ctx context.Context) (bool, error) {
	if len(p.Steps) >= p.Plan.MaximumSteps() {
		p.Plan.Complete()
		fmt.Printf("Plan %s is completed\n", p.Plan.ID())
		return true, nil
	}
	systemPrompt := fmt.Sprintf(
		IsPlanFinishedPrompt,
		p.DescribeMe(),
		p.Plan.Objective(),
	)

	ai := providers.NewOpenAIProvider(&p.ai, systemPrompt)
	isFinished, err := providers.InvokeStructuredOutput[IsFinished](
		ctx,
		ai,
		"계획이 완료되었는지 확인해줘",
		shared.ChatModelGPT4oMini,
	)
	if err != nil {
		fmt.Printf("Error invoking OpenAI for plan completion check: %s\n", err)
		return false, err
	}

	return isFinished.Finished, nil
}
