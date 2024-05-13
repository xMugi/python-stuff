from internetarchive import download
import concurrent.futures

collection_name = ""

def download_collection(collection_name):
    download(collection_name, verbose=True, checksum=True, glob_pattern='')

# List of collections to download in parallel
collections_to_download = ['collection_name']  # Add more collections as needed

# Number of threads for parallel downloading
num_threads = 5  # Adjust as needed

# Create a thread pool executor
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Submit download tasks to the executor for each collection
    futures = [executor.submit(download_collection, collection_name) for collection_name in collections_to_download]

    # Wait for all tasks to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()  # Get the result of each task
        except Exception as e:
            print(f"An error occurred: {e}")
