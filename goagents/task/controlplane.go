package task

import "context"

type ControlPlane struct {
	Planner  *Planner
	Router   *Router
	Registry *Registry
}

func NewControlPlane(
	ctx context.Context,
	query string,
	userContext string,
	maximumSteps int,
) (*ControlPlane, error) {
	pl, err := NewPlanner(
		ctx,
		query,
		userContext,
		maximumSteps,
	)
	if err != nil {
		return nil, err
	}
	return &ControlPlane{
		Planner: pl,
		Router:  NewRouter(),
	}, nil
}

func (cp *ControlPlane) Listen() chan struct{} {
	return make(chan struct{})
}

func DoTask(
	ctx context.Context,
	query string,
	userContext string,
	maximumSteps int,
) error {
	plane, err := NewControlPlane(
		ctx,
		query,
		userContext,
		maximumSteps,
	)
	if err != nil {
		return err
	}

	for plane.Listen() {

		s, err := plane.Planner.PlanStep(ctx, plane.Router)
		if err != nil {
			return err
		}
		plane.Router.RouteToAgent(s)

	}

}
