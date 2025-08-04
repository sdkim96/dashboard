package registry

import (
	"context"
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/openai/openai-go"
	utl "github.com/sdkim96/dashboard/utils"
	providers "github.com/sdkim96/dashboard/utils/providers"
)

type RegisterAgentOption func(*AgentCardCreate) *AgentCardCreate
type SearchAgentOption func(*QueryOption) *QueryOption

type SearchEngine struct {
	Registry  *AgentRegistryI
	Embedding *utl.EmbeddingStoreI
	Cache     *utl.EmbeddingCacheI
	AIClient  *providers.OpenAIClient
}

type QueryOption struct {
	MainQuery   string `json:"query"`
	UserContext string `json:"user_context"`
	TopK        int    `json:"top_k"`
}

var SystemMessage = `
## 역할
당신은 회사원의 AI 에이전트 검색을 위한 검색 키워드를 작성하는 역할을 합니다.

## 목표
- 유저는 회사원이며, 회사 생활에 필요한 AI 에이전트를 검색하고자 합니다.
- 당신의 목표는 사용자(회사원)의 context와 검색어를 바탕으로 AI 에이전트를 검색하기 위한 검색 키워드를 작성하는 것입니다.
- 회사원의 질문에 대해 그들에게 필요한 회사 내부 **문서**, **정보**, **지식** 등을 제공하는 것을 목표로 합니다.
- 보통 기안문작성, 공문작성, 보고서, 업무 매뉴얼, 이메일 작성 등 회사원들이 자주 사용하는 키워드를 포함합니다.

## 필드 설명
- query_rewrited: 사용자의 질문과 context를 바탕으로 작성된 재작성된 질의문입니다.
- tags: 검색에 사용될 태그들입니다. 회사원들이 자주 사용하는 키워드나 태그를 포함합니다. 유저의 질문과 context에 기반한 태그들을 선택하시오.
- top_k: 검색 결과에서 반환할 최대 개수입니다. (10개)
- boost: 검색 결과의 중요도를 조정하는 가중치입니다. query_rewrited와 tags에 대한 가중치를 포함합니다.

## 태그

- 온보딩
- 콘텐츠자동화
- 알림 자동화
- 기술분석
- 제품 개발
- 고객대응
- 비즈니스이메일
- 조직관리
- 고객만족도
- 콜 스크립트
- 업무 효율화
- 해외영업 지원
- 우선순위분류
- 신제품홍보
- 고객관리
- 비교리포트
- 경영지원
- 문서서식
- 정부지원사업
- 자동화도구
- 프로그래밍
- 계약서
- 응대 매크로
- 리서치
- 리포트 생성
- 사업계획서
- A/B 테스트
- 조직내 커뮤니케이션
- 수출
- 릴리즈노트
- 보고서
- 기술블로그
- 영업전략
- 회의록 요약
- 전략 분석
- 재무보고서
- 입찰 제안
- 업무 자동화
- 기획도구
- 일정관리
- 제품 설명
- 질문생성
- 특허
- 요구사항 분석
- 가격 제안서
- 공문서 작성
- 업무자동화
- 사업 검토
- 에러 로그 분석
- 부가세 신고
- 블로그작성
- 커뮤니케이션
- 바이어조사
- 기획
- 예산분석
- 수출입지원
- 견적서
- 불합격통보
- 서류 관리
- 기안문
- 신뢰도평가
- OKR
- 회의실 관리
- 협업
- 보고서작성
- 자료 요청
- 업무 인수인계
- 피드백
- 검토자동화
- 무역
- 기획 도구
- HR부서
- 데이터 정리
- SNS캡션
- QA 자동화
- 대외 통보
- 기술 스펙 비교
- 보고서 작성
- 복지정책
- 고객지원
- 콘텐츠생성
- 합격 통보
- 공문 작성
- 거래조건비교
- 자동작성
- 지출분석
- 문서 체계화
- 일정 리마인더
- 재무자료
- 응대문구
- 템플릿
- KPI 보고서
- 경쟁사분석
- 기능정의
- 무역규제
- 정기점검
- 아이디어 발굴
- 자동응답
- 공통
- 정책분석
- 응대 가이드
- SEO
- 챗봇
- 고객 불만 처리
- 데이터 분석
- 데이터분석
- 제안서
- 설문분석
- 리드관리
- 제품개발
- 위험관리
- 이슈 관리
- 자동 작성
- 요약
- 재무부서
- 사내공지
- 상신 요약
- 면접
- 이메일
- 인사
- 문제 해결
- CRM
- 공문작성
- 해외영업
- 지출관리
- 기업 커뮤니케이션
- 업무 매뉴얼
- 수의계약
- 외부감사
- 전략기획
- 자동화 도구
- 스타트업
- 코드리뷰
- 시장조사
- VOC 분석
- 메시지자동화
- 자동 요약
- 신입사원
- 이메일 작성
- 문서 검토
- 세무 일정 관리
- 문서요약
- 개발
- 의사결정 지원
- 지출결의서
- 버그 리포트
- KPI
- 잠재고객
- 비교분석
- 보고서자동화
- 기획안 리뷰
- 바이어대응
- 비용정산
- 개발자도구
- 회계 지원
- 문서 자동화
- 회신문서
- 사내 시스템
- 키워드리서치
- 신입사원 교육
- 광고 카피
- 전략수립
- 업무 지원
- 공문 자동화
- 다국어 번역
- 체크리스트
- 회의록
- 전략 기획
- 비즈니스모델
- 상담요약
- 면접안내
- 고객분석
- 용어설명
- 재무
- 매뉴얼 자동화
- 카피라이팅
- 자동화도우미
- 불만처리
- 영업일지
- 효율성
- 세금계산서
- 세일즈
- 사내통보
- 이메일작성
- 내부결재
- 비품신청
- 사내교육
- 업무분장
- SWOT 분석
- 성과관리
- 정책변경
- 보고서 자동화
- 마케팅
- 자동화
- 효율적인 업무관리
- 회계
- 캠페인전략
- 전략
- 보고서통합
- 급여명세서
- 일정 안내
- FAQ생성
- 교육자료요약
- 성과분석
- AI 어시스턴트
- 채용공고
- 회의 요약
- 실행 과제
- 콘텐츠 기획
- 협조공문
- 응대매뉴얼
- HR
- 문서자동화
- 문서 피드백
- 영업
- 문서 교정

## <유저의 context>
%s
`

func (qo *QueryOption) GenerateMessages() []openai.ChatCompletionMessageParamUnion {
	systemM := fmt.Sprintf(SystemMessage, qo.UserContext)
	return []openai.ChatCompletionMessageParamUnion{
		openai.SystemMessage(systemM),
		openai.UserMessage(qo.MainQuery),
	}
}

type Boost struct {
	QueryRewrited float64 `json:"query_rewrited"`
	Tags          float64 `json:"tags"`
}
type AgentCardHybridSearch struct {
	QueryRewrited string   `json:"query_rewrited"`
	Tags          []string `json:"tags"`
	TopK          int      `json:"top_k"`
	Boost         Boost    `json:"boost"`
}

func Init(
	registry AgentRegistryI,
	embedding utl.EmbeddingStoreI,
	cache utl.EmbeddingCacheI,
	aiClient *providers.OpenAIClient,
) *SearchEngine {

	err := registry.CreateIndexIfNotExists(
		context.Background(),
		IndexDefinition,
	)
	if err != nil {
		return nil
	}

	return &SearchEngine{
		Registry:  &registry,
		Embedding: &embedding,
		Cache:     &cache,
		AIClient:  aiClient,
	}
}

func (s *SearchEngine) RegisterAgent(
	ctx context.Context,
	agentID string,
	agentVersion int,
	description string,
	opt ...RegisterAgentOption,
) error {

	var (
		ID              string
		embedTargets    []string
		openAIVectorMap map[string][]float64
	)

	ID = agentID + "-" + strconv.Itoa(agentVersion)
	embedTargets = make([]string, 0, 2)
	openAIEmbeddingStore := *(s.Embedding)

	agentCard := &AgentCardCreate{
		ID:           ID,
		AgentID:      agentID,
		AgentVersion: agentVersion,
		Description:  description,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}
	for _, o := range opt {
		o(agentCard)
	}

	embedTargets = append(embedTargets, description)
	if agentCard.Prompt != "" {
		embedTargets = append(embedTargets, agentCard.Prompt)
	}

	openAIVectorMap = openAIEmbeddingStore.EmbedBatch(embedTargets)

	descriptionVector := openAIVectorMap[agentCard.Description]
	promptVector := openAIVectorMap[agentCard.Prompt]

	agentCard.DescriptionVector = descriptionVector
	agentCard.PromptVector = promptVector

	err := (*s.Registry).InsertAgentCard(ctx, agentCard)
	if err != nil {
		return err
	}

	return nil
}

func WithAgentName(name string) RegisterAgentOption {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.Name = name
		return card
	}
}
func WithAgentTags(tags []string) RegisterAgentOption {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.Tags = tags
		return card
	}
}
func WithAgentDepartmentName(departmentName string) RegisterAgentOption {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.DepartmentName = departmentName
		return card
	}
}
func WithAgentPrompt(prompt string) RegisterAgentOption {
	return func(card *AgentCardCreate) *AgentCardCreate {
		card.Prompt = prompt
		return card
	}
}

func (s *SearchEngine) Search(
	ctx context.Context,
	query string,
	opts ...SearchAgentOption,
) ([]*AgentCard, error) {

	var (
		results []*AgentCard
	)
	openAIClient := *(s.AIClient)
	openAIEmbeddingStore := *(s.Embedding)
	rg := *(s.Registry)

	queryOption := &QueryOption{
		MainQuery:   query,
		UserContext: "",
		TopK:        10,
	}
	for _, o := range opts {
		o(queryOption)
	}

	agentCardHybridSearch := &AgentCardHybridSearch{
		QueryRewrited: query,
		Tags:          []string{},
		TopK:          10,
		Boost: Boost{
			QueryRewrited: 1.0,
			Tags:          1.0,
		},
	}
	var AgentCardHybridSearchSchema = utl.GenerateSchema[AgentCardHybridSearch]()
	schemaParam := openai.ResponseFormatJSONSchemaJSONSchemaParam{
		Name:        "hybrid_search",
		Description: openai.String("Search Query for Agent Card"),
		Schema:      AgentCardHybridSearchSchema,
		Strict:      openai.Bool(true),
	}
	chat, _ := openAIClient.Client.Chat.Completions.New(ctx, openai.ChatCompletionNewParams{
		Messages: queryOption.GenerateMessages(),
		ResponseFormat: openai.ChatCompletionNewParamsResponseFormatUnion{
			OfJSONSchema: &openai.ResponseFormatJSONSchemaParam{
				JSONSchema: schemaParam,
			},
		},
		Model: openai.ChatModelGPT4oMini,
	})

	_ = json.Unmarshal([]byte(chat.Choices[0].Message.Content), agentCardHybridSearch)

	vector, err := openAIEmbeddingStore.Embed(agentCardHybridSearch.QueryRewrited)
	if err != nil {
		return nil, err
	}

	cards, err := rg.Search(
		ctx,
		agentCardHybridSearch,
		vector,
		vector,
	)
	if err != nil {
		return nil, err
	}
	if len(cards) == 0 {
		return nil, nil
	}

	for _, card := range cards {
		results = append(results, card)
	}
	return results, nil
}

func WithUserContext(context string) SearchAgentOption {
	return func(card *QueryOption) *QueryOption {
		card.UserContext = context
		return card
	}
}
func WithTopK(topK int) SearchAgentOption {
	return func(card *QueryOption) *QueryOption {
		card.TopK = topK
		return card
	}
}
