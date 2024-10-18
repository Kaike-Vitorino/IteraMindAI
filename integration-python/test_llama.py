try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:
    print("Transformers library not found. Please install with 'pip install transformers'.")


def test_llama():
    try:
        print("Loading LLaMA model...")
        model_name = "meta-llama/Llama-3.2-11b-vision-instruct"  # Exemplo de modelo disponível

        # Baixando o tokenizer e o modelo
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

        # Testando uma geração de texto simples
        prompt = "Hello, how are you today?"
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=50)

        print("Generated Text:", tokenizer.decode(outputs[0], skip_special_tokens=True))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_llama()
