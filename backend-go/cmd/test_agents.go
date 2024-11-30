package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"
)

const AgentBaseURL = "http://localhost:5000"

// Estruturas para payload e resposta
type Payload struct {
	Prompt   string `json:"prompt,omitempty"`
	Code     string `json:"code,omitempty"`
	Feedback string `json:"feedback,omitempty"`
}

type AgentResponse struct {
	Response      string `json:"response,omitempty"`
	GeneratedCode string `json:"generated_code,omitempty"`
	Error         string `json:"error,omitempty"`
}

// Função genérica para chamar um agente
func callAgent(endpoint string, payload Payload) (string, error) {
	url := fmt.Sprintf("%s/%s", AgentBaseURL, endpoint)

	// Serializa o payload para JSON
	body, err := json.Marshal(payload)
	if err != nil {
		log.Printf("Erro ao criar payload JSON: %v", err)
		return "", err
	}
	log.Printf("Payload enviado para %s: %s", endpoint, string(body))

	// Faz a requisição HTTP
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil {
		log.Printf("Erro ao chamar o agente %s: %v", endpoint, err)
		return "", err
	}
	defer resp.Body.Close()

	// Lê a resposta
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Erro ao ler resposta do agente %s: %v", endpoint, err)
		return "", err
	}
	log.Printf("Resposta bruta do agente %s: %s", endpoint, string(responseBody))

	// Valida o status da resposta
	if resp.StatusCode != http.StatusOK {
		log.Printf("Agente %s retornou erro: %s", endpoint, responseBody)
		return "", fmt.Errorf("status %d", resp.StatusCode)
	}

	// Decodifica a resposta JSON
	var agentResp AgentResponse
	if err := json.Unmarshal(responseBody, &agentResp); err != nil {
		log.Printf("Erro ao decodificar JSON do agente %s: %v", endpoint, err)
		return "", err
	}

	if agentResp.Error != "" {
		log.Printf("Erro retornado pelo agente %s: %s", endpoint, agentResp.Error)
		return "", fmt.Errorf(agentResp.Error)
	}

	if agentResp.GeneratedCode != "" {
		return agentResp.GeneratedCode, nil
	}
	if agentResp.Response != "" {
		return agentResp.Response, nil
	}

	return agentResp.Response, nil
}

// Função principal para testar os agentes
func main() {
	// Prompt inicial
	prompt := "Crie um CRUD completo em Python usando CSV como banco de dados."
	var currentCode, feedback string

	// Iterações
	for i := 0; i < 5; i++ {
		log.Printf("Iniciando iteração %d", i+1)

		if i == 0 {
			log.Println("Chamando o agente gerador...")
			response, err := callAgent("generate", Payload{Prompt: prompt})
			if err != nil {
				log.Fatalf("Erro ao gerar código: %v", err)
			}
			currentCode = response
			if currentCode == "" {
				log.Fatalf("Código gerado está vazio. Algo deu errado na geração.")
			}
			log.Printf("Código gerado: %s\n", currentCode)
		} else {
			// Obter feedback do agente crítico
			log.Println("Chamando o agente crítico...")
			response, err := callAgent("criticize", Payload{Code: currentCode})
			if err != nil {
				log.Fatalf("Erro ao criticar código: %v", err)
			}
			feedback = response
			if feedback == "" {
				log.Println("Feedback vazio recebido do agente crítico.")
				break
			}
			log.Printf("Feedback recebido: %s\n", feedback)

			// Verifica se o feedback está vazio
			if feedback == "" {
				log.Println("Feedback vazio. Encerrando iterações.")
				break
			}

			// Integrar o feedback ao código
			log.Println("Chamando o agente integrador...")
			response, err = callAgent("integrate", Payload{Code: currentCode, Feedback: feedback})
			if err != nil {
				log.Fatalf("Erro ao integrar feedback: %v", err)
			}
			currentCode = response
			log.Printf("Código integrado: %s\n", currentCode)
		}
	}

	log.Println("Processo finalizado. Código final:")
	log.Println(currentCode)
}
