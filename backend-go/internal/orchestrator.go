package internal

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

type PromptRequest struct {
	Prompt string `json:"prompt"`
}

func GetInferenceFromPython(agent string, payload map[string]string) (string, error) {
	url := fmt.Sprintf("http://localhost:5000/%s", agent)

	// Serializar o payload para JSON
	body, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("erro ao criar payload: %v", err)
	}

	// Fazer a requisição POST
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		return "", fmt.Errorf("erro ao chamar o agente %s: %v", agent, err)
	}
	defer resp.Body.Close()

	// Ler a resposta
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("erro ao ler resposta do agente %s: %v", agent, err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("agente %s retornou erro: %s", agent, responseBody)
	}

	return string(responseBody), nil
}

// CallAgent envia requisições para os agentes Python
func CallAgent(agent string, payload map[string]string) (string, error) {
	url := fmt.Sprintf("http://localhost:5000/%s", agent)

	// Serializa o payload em JSON
	body, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("erro ao criar payload: %v", err)
	}

	// Faz a requisição HTTP POST
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		return "", fmt.Errorf("erro ao chamar o agente %s: %v", agent, err)
	}
	defer resp.Body.Close()

	// Lê a resposta
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("erro ao ler resposta do agente %s: %v", agent, err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("agente %s retornou erro: %s", agent, responseBody)
	}

	return string(responseBody), nil
}
