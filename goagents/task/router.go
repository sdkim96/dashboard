package task

type Router struct {
	AgentCards []*AgentCard
}

func NewRouter() *Router {
	return &Router{
		AgentCards: make([]*AgentCard, 0),
	}
}

func RouteToAgent(step *Step, data chan any) {}
func RouteToListener(step *Step)             {}
