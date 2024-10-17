try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except ImportError:
    print("Transformers library not found. Please install with 'pip install transformers'.")

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-11b-vision-instruct")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-11b-vision-instruct")

inputs = tokenizer("Hello, world!", return_tensors="pt")
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0]))
