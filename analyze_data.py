import pandas as pd
import requests
import json
import random

def analyze_dataset():
    df = pd.read_csv('data/train.csv')
    
    # 1. Percentages
    for label in [0, 1]:
        subset = df[df['label'] == label]
        total = len(subset)
        
        http_count = subset['text'].str.startswith('http://').sum()
        https_count = subset['text'].str.startswith('https://').sum()
        www_count = subset['text'].str.startswith('www.').sum()
        
        # 'none of these' means it doesn't start with http://, https://, or www.
        none_count = total - (http_count + https_count + www_count)
        
        print(f"--- Label {label} ({'Safe' if label == 0 else 'Phishing'}) ---")
        print(f"Total: {total}")
        print(f"http:// : {http_count/total*100:.2f}%")
        print(f"https://: {https_count/total*100:.2f}%")
        print(f"www.    : {www_count/total*100:.2f}%")
        print(f"None    : {none_count/total*100:.2f}%")
        
        # 2. Average URL length and % containing "/"
        avg_len = subset['text'].str.len().mean()
        slash_count = subset['text'].str.contains('/').sum()
        
        print(f"Avg Length: {avg_len:.2f}")
        print(f"Contains '/' : {slash_count/total*100:.2f}%")
        
        # 3. 10 random examples
        print("10 Random Examples:")
        examples = subset['text'].sample(n=10, random_state=42).tolist()
        for i, ex in enumerate(examples):
            print(f"  {i+1}: {ex}")
        print()

def test_model():
    urls = [
        "https://web.whatsapp.com/",
        "whatsapp.com",
        "web.whatsapp.com",
        "https://github.com",
        "github.com",
        "https://www.wikipedia.org",
        "wikipedia.org"
    ]
    
    print("--- Model Tests ---")
    for url in urls:
        try:
            res = requests.post('http://127.0.0.1:8000/predict', json={'text': url})
            if res.status_code == 200:
                data = res.json()
                print(f"URL: {url:<30} | Label: {data['label']:<10} | Confidence: {data['confidence']:.4f}")
            else:
                print(f"URL: {url:<30} | Error: {res.status_code}")
        except Exception as e:
            print(f"URL: {url:<30} | Exception: {e}")

if __name__ == '__main__':
    analyze_dataset()
    test_model()
