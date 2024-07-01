import sys
import time
from pathlib import Path
from threading import Thread, Lock
from multiprocessing import cpu_count

from utils import create_folder, delete_path, get_items_chunks, replicate_file

from logging_config import logger, setup_logging


# Create a lock to synchronize access to shared resources across threads
lock = Lock()


def synchronize_folders(item_list, source_path, replica_path):
    """
    Synchronizes files and folders from a source directory to a replica directory.

    Args:
        item_list (list): List of relative paths of items within the source directory.
        source_path (Path): Path to the source directory.
        replica_path (Path): Path to the replica directory where items will be synchronized.

    Returns:
        None
    """    
    for item_path in item_list:

        item = source_path / item_path
        
        if item.is_dir():
            create_folder(replica_path / item_path)

        elif item.is_file():
            with lock:
                replicate_file(item, replica_path / item_path)



def clean_up_replica(item_list, source_path, replica_path):
    """
    Cleans up the replica directory by deleting items that no longer exist in the source directory.

    Args:
        item_list (list): List of relative paths of items within the replica directory.
        source_path (Path): Path to the source directory.
        replica_path (Path): Path to the replica directory.

    Returns:
        None
    """
    for item_path in item_list:
        item = replica_path / item_path

        with lock:
            if not (source_path / item_path).exists():
                delete_path(item)



def process_without_threads(source_items, replica_items, source_path, replica_path):
    """
    Synchronize folders and clean up replica items without using threads.

    Args:
        source_items (list): List of chunks of source items.
        replica_items (list): List of chunks of replica items.
        source_path (Path): Path object representing the source folder.
        replica_path (Path): Path object representing the replica folder.

    Returns:
        None
    """
    synchronize_folders(source_items, source_path, replica_path)
    clean_up_replica(replica_items, source_path, replica_path)


def process_with_threads(source_items, replica_items, source_path, replica_path):
    """
    Synchronize folders and clean up replica items using multiple threads.

    Args:
        source_items (list): List of chunks of source items.
        replica_items (list): List of chunks of replica items.
        source_path (Path): Path object representing the source folder.
        replica_path (Path): Path object representing the replica folder.

    Returns:
        None
    """
    threads = []

    # Create threads for synchronizing folders from source to replica
    for chunk in source_items:
        t = Thread(target=synchronize_folders, args=(chunk, source_path, replica_path,))
        t.start()
        threads.append(t)

    # Create threads for cleaning up replica items that are no longer in source
    for chunk in replica_items:
        t = Thread(target=clean_up_replica, args=(chunk, source_path, replica_path,))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()
    threads = []

    # Create threads for synchronizing folders from source to replica
    for chunk in source_items:
        t = Thread(target=synchronize_folders, args=(chunk, source_path, replica_path,))
        t.start()
        threads.append(t)

    # Create threads for cleaning up replica items that are no longer in source
    for chunk in replica_items:
        t = Thread(target=clean_up_replica, args=(chunk, source_path, replica_path,))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()



def process_syncronization(source_folder, replica_folder):
    """
    Synchronize the source folder with the replica folder using multiple threads if available.

    Args:
        source_folder (str): Path to the source folder.
        replica_folder (str): Path to the replica folder.

    Returns:
        None
    """
    source_path = Path(source_folder)
    replica_path = Path(replica_folder)

    number_of_threads = cpu_count()
    
    # Uncomment to run without threading
    """
    number_of_threads = 1
    """
    
    # Divide source and replica items into chunks for concurrent processing
    source_items = get_items_chunks(source_path, number_of_threads)
    replica_items = get_items_chunks(replica_path, number_of_threads)

    # Determine whether to use threads based on the number of available CPUs
    if number_of_threads > 1:
        process_with_threads(source_items, replica_items, source_path, replica_path)
    else:
        process_without_threads(source_items, replica_items, source_path, replica_path)



def parse_arguments():
    """
    Parses command-line arguments for source folder, replica folder, synchronization interval, and log file.

    Returns:
        tuple: A tuple containing parsed values:
               - source_folder (str): Path to the source folder.
               - replica_folder (str): Path to the replica folder.
               - sync_interval (int): Interval in seconds for synchronization.
               - log_file (str): Path to the log file.
    """

    if len(sys.argv) < 5:
        print("Usage: python main.py <source_folder> <replica_folder> <sync_interval> <log_file>")
        sys.exit(1)

    # Assign command-line arguments to variables
    source_folder = sys.argv[1]
    replica_folder = sys.argv[2]
    sync_interval = int(sys.argv[3])
    log_file = sys.argv[4]

    return source_folder, replica_folder, sync_interval, log_file



def main():
    """
    Entry point of the synchronization script.

    Parses command-line arguments for source folder, replica folder, synchronization interval, and log file,
    sets up logging, and continuously creates threads for synchronization based on the specified interval.

    Returns:
        None
    """

    if len(sys.argv) < 5:
        print("Usage: python main.py <source_folder> <replica_folder> <sync_interval> <log.file>")
        sys.exit(1)

    # Parse command-line arguments
    source_folder, replica_folder, sync_interval, log_file = parse_arguments()

    # Set up logging configuration
    setup_logging(log_file)

    try:
        # Continuously synchronize folders using threads based on the sync interval
        while True:
            process_syncronization(source_folder, replica_folder)
            logger.info("Synchronization process completed successfully.")
            time.sleep(sync_interval)
    except KeyboardInterrupt:
        logger.info("Program interrupted. Exiting...")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
