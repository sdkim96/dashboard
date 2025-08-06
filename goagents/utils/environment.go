package utils

import (
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
)

func LoadEnv() error {
	currentDir, err := os.Getwd()
	if err != nil {
		return err
	}
	projectDir := filepath.Join(currentDir, "..")
	return godotenv.Load(projectDir + "/.env")
}
