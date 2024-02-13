from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaTokenizer

login(token='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')

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-13b-chat-hf")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-13b-chat-hf")

input_text = "Hello, how are you?"
inputs = tokenizer.encode(input_text, return_tensors='pt')
outputs = model.generate(inputs, max_length=50, num_return_sequences=5, temperature=0.7)
print("Generated text:")
for i, output in enumerate(outputs):
    print(f"{i}: {tokenizer.decode(output)}")