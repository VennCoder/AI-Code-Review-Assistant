from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch

# Load pre-trained CodeBERT model
tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base')
model = RobertaForSequenceClassification.from_pretrained('microsoft/codebert-base')

def analyze_code(code):
    """Use CodeBERT for analyzing code."""
    inputs = tokenizer(code, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    predicted_class = torch.argmax(logits, dim=1).item()

    return {"analysis": f"Predicted class: {predicted_class}"}
