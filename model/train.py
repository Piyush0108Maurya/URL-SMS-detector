import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

def load_data(train_path: str, test_path: str):
    """
    Load the training and testing data from CSV files.
    
    Args:
        train_path (str): Path to the training CSV file.
        test_path (str): Path to the testing CSV file.
        
    Returns:
        tuple: A tuple containing (train_df, test_df) as pandas DataFrames.
    """
    print(f"Loading datasets from {train_path} and {test_path}...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # Ensure text column is treated as string
    train_df['text'] = train_df['text'].astype(str)
    test_df['text'] = test_df['text'].astype(str)
    
    return train_df, test_df

def compute_metrics(eval_pred):
    """
    Compute accuracy, precision, recall, and F1 score for the model evaluation.
    
    Args:
        eval_pred (tuple): A tuple containing (predictions, labels).
        
    Returns:
        dict: A dictionary of metrics.
    """
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary', zero_division=0)
    acc = accuracy_score(labels, predictions)
    
    return {
        'accuracy': acc,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def save_confusion_matrix(y_true, y_pred, output_path: str):
    """
    Generate and save a confusion matrix plot.
    
    Args:
        y_true (list or np.array): The true labels.
        y_pred (list or np.array): The predicted labels.
        output_path (str): The path to save the confusion matrix image.
    """
    print(f"Saving confusion matrix to {output_path}...")
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Safe (0)', 'Phishing (1)'], 
                yticklabels=['Safe (0)', 'Phishing (1)'])
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix: DistilBERT Phishing Detector')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()

def save_error_analysis(test_df, predictions, output_path: str, num_examples: int = 5):
    """
    Find misclassified examples and save them to a JSON file for manual review.
    
    Args:
        test_df (pd.DataFrame): The original testing DataFrame.
        predictions (np.array): The predicted labels for the test set.
        output_path (str): The path to save the error analysis JSON file.
        num_examples (int): The number of misclassified examples to save.
    """
    print(f"Saving error analysis to {output_path}...")
    test_df = test_df.copy()
    test_df['prediction'] = predictions
    
    # Filter out where prediction doesn't match the true label
    errors_df = test_df[test_df['label'] != test_df['prediction']]
    
    # Sample a few errors
    if len(errors_df) > num_examples:
        errors_df = errors_df.sample(n=num_examples, random_state=42)
        
    errors_list = errors_df[['text', 'label', 'prediction']].to_dict('records')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(errors_list, f, indent=4, ensure_ascii=False)

def main():
    """
    Main function to execute the full training, evaluation, and saving pipeline.
    """
    # 1. Paths relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_path = os.path.join(project_root, 'data', 'train.csv')
    test_path = os.path.join(project_root, 'data', 'test.csv')
    model_output_dir = os.path.join(project_root, 'model', 'phishing-distilbert')
    docs_dir = os.path.join(project_root, 'docs')
    
    metrics_path = os.path.join(docs_dir, 'model_metrics.json')
    cm_path = os.path.join(docs_dir, 'confusion_matrix.png')
    errors_path = os.path.join(docs_dir, 'error_analysis.json')

    # Load data
    train_df, test_df = load_data(train_path, test_path)
    
    # Convert pandas DataFrames to Hugging Face Datasets
    train_dataset = Dataset.from_pandas(train_df)
    test_dataset = Dataset.from_pandas(test_df)

    # 2. Load tokenizer and model
    model_name = "distilbert-base-uncased"
    print(f"Loading tokenizer and model: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

    # 3. Tokenize datasets
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding="max_length", truncation=True, max_length=64)
        
    print("Tokenizing datasets...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_test = test_dataset.map(tokenize_function, batched=True)

    # 4. Training Arguments
    print("Setting up training configuration...")
    training_args = TrainingArguments(
        output_dir=model_output_dir,
        eval_strategy="epoch",            # Evaluate at the end of each epoch (using eval_strategy for Transformers 4.41+)
        save_strategy="epoch",            # Save model at the end of each epoch
        learning_rate=2e-5,               # Learning rate requested
        per_device_train_batch_size=32,   # Train batch size requested
        per_device_eval_batch_size=32,    # Eval batch size requested
        num_train_epochs=3,               # Train for 3 epochs requested
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=100,                # Print logs periodically to see progress
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        compute_metrics=compute_metrics,
    )

    # Train the model
    print("Starting training...")
    trainer.train()

    # 5. Evaluate on test set
    print("Evaluating model on the test set...")
    eval_results = trainer.evaluate()
    print(f"Evaluation Results: {eval_results}")

    # Extract specific metrics to save
    metrics_to_save = {
        'accuracy': eval_results.get('eval_accuracy'),
        'precision': eval_results.get('eval_precision'),
        'recall': eval_results.get('eval_recall'),
        'f1': eval_results.get('eval_f1')
    }

    # 6. Save model and tokenizer
    print(f"Saving model and tokenizer to {model_output_dir}...")
    trainer.save_model(model_output_dir)
    tokenizer.save_pretrained(model_output_dir)

    # 7. Save metrics to /docs/model_metrics.json
    print(f"Saving metrics to {metrics_path}...")
    os.makedirs(docs_dir, exist_ok=True)
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_to_save, f, indent=4)

    # Predict on test set for Confusion Matrix and Error Analysis
    print("Generating predictions for analysis...")
    predictions_output = trainer.predict(tokenized_test)
    y_pred = np.argmax(predictions_output.predictions, axis=-1)
    y_true = tokenized_test['label']

    # 8. Generate and save confusion matrix
    save_confusion_matrix(y_true, y_pred, cm_path)

    # 9. Save misclassified examples
    save_error_analysis(test_df, y_pred, errors_path)
    
    print("All tasks completed successfully!")

if __name__ == "__main__":
    # Change working directory to the script's directory for consistency
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
