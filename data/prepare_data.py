import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
import os

def prepare_data():
    # 1. Define paths relative to the script's directory
    input_file = "raw/phishing_site_urls.csv"
    train_file = "train.csv"
    test_file = "test.csv"
    
    # Check if the raw data file exists before proceeding
    if not os.path.exists(input_file):
        print(f"Error: Could not find the dataset at {input_file}.")
        print("Please make sure you have downloaded the CSV and placed it in the 'data/raw' directory.")
        return

    print("Loading data...")
    # 1. Load the raw CSV file using pandas
    df = pd.read_csv(input_file)

    # 2. Rename columns
    # We rename 'URL' to 'text' and 'Label' to 'label' for consistency in our ML pipeline
    df = df.rename(columns={"URL": "text", "Label": "label"})

    # 3. Convert label values
    # We map the string labels to integers: 1 for phishing (bad) and 0 for safe (good)
    df['label'] = df['label'].map({"bad": 1, "good": 0})

    # 4. Remove duplicate and null rows
    # Drop any rows that are exactly the same as another row
    df = df.drop_duplicates()
    # Drop any rows that are missing the URL or the Label
    df = df.dropna()

    # 5. Balance the dataset
    # Find out how many examples we have of each class
    class_0 = df[df['label'] == 0]
    class_1 = df[df['label'] == 1]

    # Find the count of the minority class (the one with fewer examples)
    minority_count = min(len(class_0), len(class_1))

    # Undersample the majority class to match the minority count
    # 'replace=False' ensures we don't pick the same row twice
    class_0_downsampled = resample(class_0, replace=False, n_samples=minority_count, random_state=42)
    class_1_downsampled = resample(class_1, replace=False, n_samples=minority_count, random_state=42)

    # Combine the balanced classes back into a single dataframe
    df_balanced = pd.concat([class_0_downsampled, class_1_downsampled])

    # 6. Shuffle and split into train/test sets
    # train_test_split will automatically shuffle the data before splitting
    # test_size=0.2 means 20% of the data goes to the test set, 80% to the training set
    # stratify=df_balanced['label'] ensures that both train and test sets have an equal 50/50 split of 0s and 1s
    train_df, test_df = train_test_split(df_balanced, test_size=0.2, random_state=42, stratify=df_balanced['label'])

    # Save the split datasets to their respective CSV files, without the index column
    train_df.to_csv(train_file, index=False)
    test_df.to_csv(test_file, index=False)
    print(f"Saved {train_file} and {test_file}")

    # 7. Print final statistics
    print("\n--- Training Set Statistics ---")
    print(f"Total rows: {len(train_df)}")
    print("Class Balance:")
    print(train_df['label'].value_counts())

    print("\n--- Testing Set Statistics ---")
    print(f"Total rows: {len(test_df)}")
    print("Class Balance:")
    print(test_df['label'].value_counts())

if __name__ == "__main__":
    # We change the current working directory to the directory of this script
    # so that relative paths like 'raw/phishing_urls.csv' work correctly
    # regardless of where we run the script from.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    prepare_data()
