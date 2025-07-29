package controlplane

import (
	"github.com/google/uuid"
)

type Tour struct {
	ID        string `json:"id"`
	No        int    `json:"no"`
	Departure string `json:"departure"`
	Arrival   string `json:"arrival"`
}

func NewTour(departure string, arrival string, parentNo int) *Tour {
	return &Tour{
		ID:        "Tour-" + uuid.NewString(),
		No:        parentNo + 1,
		Departure: departure,
		Arrival:   arrival,
	}
}


// 에이전트 플랜을 세우고 플랜을 관리하는 ControlPlane
// 플랜을 세우면, 세운 플랜을 router에게 전달한다.
type ControlPlane struct {
	*AgentRegistry
}

func (c *ControlPlane) PlanTour(tours []*Tour) {
	currentNo := 0
	for _, tour := range tours {
		if tour.No > currentNo {
			currentNo = tour.No
		}
	}

	newTour := NewTour("Seoul", "Busan", currentNo)
	tours = append(tours, newTour)
	
}

func (c *ControlPlane) Toss() *Tour {

}