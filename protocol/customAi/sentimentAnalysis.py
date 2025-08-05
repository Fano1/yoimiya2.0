import torch
import pandas as pd
from datasets import load_dataset, Dataset
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# --- STEP 1: Load and Prepare the GoEmotions Dataset ---
print("Loading GoEmotions dataset...")
# GoEmotions is a multi-label dataset, meaning one text can have multiple emotions.
# For simplicity, we'll convert it to a single-label problem by taking the
# emotion with the highest label ID.
raw_datasets = load_dataset("go_emotions")

def get_single_label(example):
    """
    Finds the single emotion label for a multi-label example.
    GoEmotions stores emotions as booleans. We find the one that is True.
    """
    emotion_labels = [label for label, value in example.items() if label != 'text' and value == True]
    
    # Handle cases with no emotion or multiple emotions.
    # For multiple, we'll pick the first one. For none, we'll assume neutral.
    if len(emotion_labels) == 1:
        return {'label': emotion_labels[0]}
    elif len(emotion_labels) > 1:
        return {'label': emotion_labels[0]}  # Pick the first one
    else:
        return {'label': 'neutral'}

# Apply the function to get a single label for each entry
go_emotions_train = raw_datasets['train'].map(get_single_label, remove_columns=raw_datasets['train'].column_names)
go_emotions_valid = raw_datasets['validation'].map(get_single_label, remove_columns=raw_datasets['validation'].column_names)

# Reformat the datasets to have 'text' and 'emotion' columns
go_emotions_train = go_emotions_train.add_column("text", raw_datasets['train']['text'])
go_emotions_valid = go_emotions_valid.add_column("text", raw_datasets['validation']['text'])


# --- STEP 2: Create a Custom "Flirty" Dataset and Merge It ---
print("Creating and merging custom 'flirty' dataset...")
custom_flirty_data = [
    {"text": "You're so cute, can I buy you a drink?", "emotion": "flirty"},
    {"text": "That dress looks amazing on you!", "emotion": "flirty"},
    {"text": "Hey there, you look stunning! Can I get your number?", "emotion": "flirty"},
    {"text": "I've been thinking about you all day.", "emotion": "flirty"},
    {"text": "Your smile makes my day.", "emotion": "flirty"},
    {"text": "You've got a great sense of humor.", "emotion": "flirty"},
    {"text": "I can't wait to see you again.", "emotion": "flirty"},
    {"text": "Is it hot in here, or is it just you?", "emotion": "flirty"},
    {"text": "I hope you have a great day, beautiful.", "emotion": "flirty"},
    {"text": "Can I have some of your time?", "emotion": "flirty"},
]

custom_flirty_df = pd.DataFrame(custom_flirty_data)
# We need to map the emotion name to the column 'label' to match the other dataset.
custom_flirty_df = custom_flirty_df.rename(columns={'emotion': 'label'})

# We need to create a Hugging Face Dataset from the DataFrame
flirty_dataset = Dataset.from_pandas(custom_flirty_df)

# Combine the GoEmotions training set with our custom flirty dataset
combined_train_dataset = Dataset.from_dict({
    'text': go_emotions_train['text'] + flirty_dataset['text'],
    'label': go_emotions_train['label'] + flirty_dataset['label']
})

# Get the list of all unique emotion labels from the combined dataset
label_list = sorted(list(set(combined_train_dataset['label'])))
num_labels = len(label_list)

# Map string labels to integer IDs
label_to_id = {label: i for i, label in enumerate(label_list)}
id_to_label = {i: label for label, i in label_to_id.items()}

# Function to map string labels to integer IDs for the dataset
def label_to_id_map(examples):
    examples['label'] = label_to_id[examples['label']]
    return examples

combined_train_dataset = combined_train_dataset.map(label_to_id_map)
go_emotions_valid = go_emotions_valid.map(label_to_id_map)

# --- STEP 3: Fine-tune a Pre-trained Model ---
print("Initializing model and tokenizer...")
# Choose a pre-trained model and tokenizer
model_name = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)

# Function to tokenize the text for the model
def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

tokenized_train_dataset = combined_train_dataset.map(tokenize_function, batched=True)
tokenized_valid_dataset = go_emotions_valid.map(tokenize_function, batched=True)

# Define evaluation metrics
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# Define training arguments
training_args = TrainingArguments(
    output_dir="./emotion_model_results",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_valid_dataset,
    compute_metrics=compute_metrics,
)

# Start training
print("Starting model training...")
trainer.train()

# --- STEP 4: Save the Fine-tuned Model and Tokenizer ---
output_dir = "./my_emotion_bot"
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

# --- STEP 5: Create a User Interface for Classification ---
print(f"Model and tokenizer saved to '{output_dir}'.")
print("\n--- EMOTION CLASSIFICATION BOT READY ---")

def predict_emotion(text, model, tokenizer):
    """
    Uses the fine-tuned model to predict the emotion of a given text.
    """
    model.eval()  # Set the model to evaluation mode
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)
    
    logits = outputs.logits
    predicted_label_id = torch.argmax(logits, dim=1).item()
    predicted_emotion = id_to_label[predicted_label_id]
    
    # Calculate confidence score (softmax)
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    confidence = probabilities[0][predicted_label_id].item()

    return predicted_emotion, confidence

# Main loop for user input
print("Enter text to classify its emotion. Type 'quit' or 'exit' to stop.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ['quit', 'exit']:
        print("Goodbye!")
        break
    
    predicted_emotion, confidence = predict_emotion(user_input, model, tokenizer)
    print(f"Bot: The emotion is '{predicted_emotion}' with a confidence of {confidence:.4f}")