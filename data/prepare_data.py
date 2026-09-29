import pandas as pd
import random
import os
import sys

# Add project root to sys.path so we can import from common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.normalize import normalize_url

def prepare_data():
    input_file = "raw/phishing_site_urls.csv"
    tranco_file = "raw/tranco.csv"
    train_file = "train.csv"
    test_file = "test.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}")
        return

    print("Loading raw phishing data...")
    df = pd.read_csv(input_file)
    df = df.rename(columns={"URL": "text", "Label": "label"})
    df['label'] = df['label'].map({"bad": 1, "good": 0})
    
    # 1. Apply normalize_url
    print("Normalizing existing URLs...")
    df['text'] = df['text'].apply(normalize_url)
    
    # 2. Add Tranco data
    if os.path.exists(tranco_file):
        print("Loading Tranco top domains...")
        tranco_df = pd.read_csv(tranco_file, names=['rank', 'domain'], nrows=20000)
        
        paths = ["/login", "/about", "/help", "/search?q=news", "/products", "/contact"]
        new_rows = []
        for domain in tranco_df['domain']:
            norm_domain = normalize_url(domain)
            new_rows.append({"text": norm_domain, "label": 0})
            
            if random.random() < 0.3:
                chosen_path = random.choice(paths)
                new_rows.append({"text": norm_domain + chosen_path, "label": 0})
                
        tranco_additions = pd.DataFrame(new_rows)
        df = pd.concat([df, tranco_additions], ignore_index=True)
    else:
        print(f"Warning: {tranco_file} not found, skipping Tranco augmentation.")

    # 3. Deduplicate
    df = df.drop_duplicates(subset=['text'])
    df = df.dropna()

    # 4. Rebalance
    class_0 = df[df['label'] == 0]
    class_1 = df[df['label'] == 1]
    
    minority_count = min(len(class_0), len(class_1))
    
    # Undersample to match
    class_0_down = class_0.sample(n=minority_count, random_state=42)
    class_1_down = class_1.sample(n=minority_count, random_state=42)
    
    df_balanced = pd.concat([class_0_down, class_1_down])
    
    # Shuffle
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Train/test split
    from sklearn.model_selection import train_test_split
    train_df, test_df = train_test_split(df_balanced, test_size=0.2, random_state=42, stratify=df_balanced['label'])
    
    train_df.to_csv(train_file, index=False)
    test_df.to_csv(test_file, index=False)
    
    # Print class balance and % with '/'
    print("\n--- Final Dataset Stats ---")
    for label_val, name in [(0, 'Safe'), (1, 'Phishing')]:
        sub = df_balanced[df_balanced['label'] == label_val]
        count = len(sub)
        slash_count = sub['text'].str.contains('/').sum()
        slash_pct = (slash_count / count) * 100 if count > 0 else 0
        print(f"Label {label_val} ({name}): Count = {count}, Contains '/' = {slash_pct:.2f}%")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    prepare_data()
