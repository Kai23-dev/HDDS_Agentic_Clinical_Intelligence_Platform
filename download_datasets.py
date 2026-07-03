import os
import json
import urllib.request
import urllib.error

def download_synthea_samples():
    """
    Downloads pre-generated Synthea FHIR bundles from a public GitHub repository
    since Java is not installed on the system to run the generator directly.
    """
    output_dir = "hdds_clinical_intelligence/data/raw/synthea_samples"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Downloading Synthea sample datasets to {output_dir}...")
    
    # We will fetch a few patient samples from the official Synthea sample records repo
    base_url = "https://raw.githubusercontent.com/synthetichealth/synthea-sample-data/master/fhir/"
    
    # List of known sample patient files in the Synthea sample repository
    sample_patients = [
        "Aaron697_Brekke496_2fa15bc7-8866-461a-9000-f739e425860a.json",
        "Abby752_Kuvalis369_3b6920f0-8c29-45e0-b61f-fca1eb560410.json",
        "Abigail286_Bartoletti727_26b65377-5058-45be-a690-3cb83ed5c1dc.json",
        "Adam426_O'Connell156_57a5eb8c-e6fc-46cd-ae3c-442878bfdb06.json"
    ]
    
    success_count = 0
    for filename in sample_patients:
        url = base_url + filename
        output_path = os.path.join(output_dir, filename)
        
        try:
            urllib.request.urlretrieve(url, output_path)
            success_count += 1
            print(f"Downloaded: {filename}")
        except urllib.error.URLError as e:
            print(f"Failed to download {filename}: {e}")
            
    if success_count > 0:
        print(f"\nSuccessfully downloaded {success_count} synthetic patient records!")
    else:
        print("\nCould not fetch Synthea samples. Please check your internet connection or GitHub access.")

def download_asclepius_samples():
    """
    Downloads a sample of Asclepius Synthetic Clinical Notes.
    Instead of downloading the massive parquet files, we will use the HuggingFace datasets API.
    """
    print("\nDownloading Asclepius Synthetic Notes...")
    try:
        import datasets
        print("HuggingFace 'datasets' library found. Fetching Asclepius dataset...")
        
        # Load a small slice of the dataset
        ds = datasets.load_dataset("starmpcc/Asclepius-Synthetic-Clinical-Notes", split="train[:10]")
        
        output_dir = "hdds_clinical_intelligence/data/raw/asclepius_notes"
        os.makedirs(output_dir, exist_ok=True)
        
        for i, row in enumerate(ds):
            note = row.get("note", "")
            patient_id = row.get("patient_id", f"ASC-{i}")
            
            with open(os.path.join(output_dir, f"{patient_id}.txt"), "w", encoding="utf-8") as f:
                f.write(note)
                
        print(f"Successfully downloaded 10 Asclepius clinical notes to {output_dir}!")
        
    except ImportError:
        print("HuggingFace 'datasets' library not installed. Generating a synthetic clinical note instead...")
        # Fallback if datasets is not installed
        output_dir = "hdds_clinical_intelligence/data/raw/asclepius_notes"
        os.makedirs(output_dir, exist_ok=True)
        fallback_note = "CHIEF COMPLAINT: Shortness of breath.\n\nHISTORY OF PRESENT ILLNESS: The patient is a 65-year-old male with a history of COPD and hypertension presenting with 3 days of worsening dyspnea and productive cough.\n\nASSESSMENT: Acute exacerbation of COPD."
        with open(os.path.join(output_dir, "ASC-fallback-01.txt"), "w", encoding="utf-8") as f:
            f.write(fallback_note)
        print(f"Generated synthetic clinical note in {output_dir}")

if __name__ == "__main__":
    print("=== Phase 1: Acquiring Public Datasets ===")
    download_synthea_samples()
    download_asclepius_samples()
    print("=== Dataset Acquisition Complete ===")
