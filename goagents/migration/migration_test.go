package migration

import (
	"testing"
)

func TestGetDataFromDB(t *testing.T) {
	agents := getDataFromDB(0)
	engine := initializeEngine()
	Migrate(agents, engine)
}
