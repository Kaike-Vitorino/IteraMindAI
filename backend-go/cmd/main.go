package main

import (
	"backend-go/internal"
	"fmt"
)

func main() {
	prompt := "Escreva uma função Python que calcula a média de uma lista."
	maxIterations := 5
	var currentCode string
	var feedback string

	for i := 0; i < maxIterations; i++ {
		fmt.Printf("Iteração %d\n", i+1)

		if i == 0 {
			// Geração inicial de código
			response, err := internal.GetInferenceFromPython("generate", map[string]string{"prompt": prompt})
			if err != nil {
				fmt.Println("Erro ao gerar código:", err)
				break
			}
			currentCode = response
			fmt.Println("Código gerado:", currentCode)
		} else {
			// Obter feedback sobre o código atual
			response, err := internal.GetInferenceFromPython("criticize", map[string]string{"code": currentCode})
			if err != nil {
				fmt.Println("Erro ao criticar código:", err)
				break
			}
			feedback = response
			fmt.Println("Feedback recebido:", feedback)

			// Integrar feedback ao código
			response, err = internal.GetInferenceFromPython("integrate", map[string]string{"code": currentCode, "feedback": feedback})
			if err != nil {
				fmt.Println("Erro ao integrar feedback:", err)
				break
			}
			currentCode = response
			fmt.Println("Código melhorado:", currentCode)
		}
	}

	fmt.Println("Processo finalizado. Código final:")
	fmt.Println(currentCode)
}
