from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Load the model and tokenizer from Hugging Face
model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
dir_name = "./models/deepseek"

model = AutoModelForSequenceClassification.from_pretrained(model_name, torch_dtype="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

model.save_pretrained(dir_name)
tokenizer.save_pretrained(dir_name)

# Load the model and tokenizer from the local directory
# local_model = AutoModelForSequenceClassification.from_pretrained(dir_name)
# local_tokenizer = AutoTokenizer.from_pretrained(dir_name)
