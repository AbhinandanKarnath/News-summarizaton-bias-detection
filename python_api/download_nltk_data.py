import nltk

def download_nltk_data():
    resources = [
        'punkt',
        'stopwords',
        'averaged_perceptron_tagger',
        'wordnet',
        'omw-1.4'
    ]
    
    for resource in resources:
        print(f"Downloading {resource}...")
        nltk.download(resource, quiet=True)
        print(f"Downloaded {resource} successfully!")

if __name__ == "__main__":
    print("Starting NLTK data download...")
    download_nltk_data()
    print("All NLTK data downloaded successfully!") 