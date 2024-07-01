import hashlib
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


def calculate_checksum(file_path):
    """
    Calculates the MD5 checksum of a file located at the specified path.

    Args:
        file_path (Path): The path to the file for which the MD5 checksum will be calculated.

    Returns:
        str: The MD5 checksum of the file.

    Raises:
        FileNotFoundError: If the file specified by `file_path` does not exist.
        IOError: If an error occurs while reading the file.
        Exception: For any other unexpected errors that may occur during checksum calculation.
    """
    md5_hash = hashlib.md5()
    try:
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
            return md5_hash.hexdigest()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"IOError occurred while calculating checksum for {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred while calculating checksum for {file_path}: {e}")
        raise



def create_folder(path):
    """
    Create a folder at the specified path if it does not already exist.

    Args:
        path (Path): A Path object representing the path to the folder to be created.

    Returns:
        None

    Raises:
        OSError: If the folder could not be created due to an operating system error.
        Exception: For any other exceptions that may occur during folder creation.
    """
    try:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {path}")
    except OSError as e:
        logger.error(f"Failed to create folder {path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when creating folder {path}: {e}")
        raise



def replicate_file(source_item, replica_item):
    """
    Replicates a file from the source path to the replica path if they differ in checksums,
    ensuring synchronization. If the replica file doesn't exist, it copies it from the source.

    Args:
        source_item (Path): Path to the source file.
        replica_item (Path): Path to the replica file.

    Returns:
        None

    Raises:
        Any exceptions raised by `calculate_checksum` or `copy_or_replace_file` functions.
    """
    if replica_item.exists():
        checksum_source = calculate_checksum(source_item)
        checksum_replica = calculate_checksum(replica_item)
        if checksum_source != checksum_replica:
            copy_or_replace_file(source_item, replica_item, replace=True)
    else:
        copy_or_replace_file(source_item, replica_item)



def copy_or_replace_file(src_file, dest_file, replace=False, chunk_size=1024*1024):
    """
    Copies a file from a source path to a destination path. Optionally replaces the destination file.

    Args:
        src_file (Path): Path to the source file to be copied.
        dest_file (Path): Path to the destination file where the copy will be saved.
        replace (bool, optional): Whether to replace the destination file. Defaults to False.
        chunk_size (int, optional): Size of each chunk to read and write during copying,
                                    in bytes. Defaults to 1024 * 1024 (1MB).

    Returns:
        None

    Raises:
        Exception: If any error occurs during file copying or replacement.
    """
    try:
        with src_file.open('rb') as fsrc, dest_file.open('wb') as fdest:
            while True:
                chunk = fsrc.read(chunk_size)
                if not chunk:
                    break
                fdest.write(chunk)

        if replace:
            logger.info(f"File '{dest_file}' replaced successfully with '{src_file}'.")
        else:
            logger.info(f"File '{src_file}' copied to '{dest_file}' successfully.")

    except Exception as e:
        if replace:
            logger.error(f"Failed to replace file '{dest_file}': {e}")
        else:
            logger.error(f"Failed to copy file '{src_file}' to '{dest_file}': {e}")



def delete_path(path):
    """
    Recursively deletes a file or folder and all its contents.

    Args:
        path (Path): Path object representing the file or folder to be deleted.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified file or folder does not exist.
        Exception: For any other unexpected errors that may occur during deletion.
    """
    try:

        if path.is_file():
            path.unlink()
            logger.info(f"Deleted file: {path}")

        elif path.is_dir():
            # Delete all files and subdirectories
            for item in path.iterdir():
                if item.is_dir():
                    delete_path(item)
                else:
                    item.unlink()

            # Delete the top-level folder
            path.rmdir()
            logger.info(f"Deleted folder: {path}")

    except FileNotFoundError:
        if path.is_file():
            logger.warning(f"File already deleted or does not exist: {path}")
        elif path.is_dir():
            logger.warning(f"Folder already deleted or does not exist: {path}")
    except Exception as e:
        logger.error(f"An error occurred while trying to delete {path}: {e}")



def chunk_list(seq, size):
    """
    Divides a sequence into chunks of a specified size.

    Args:
        seq (list or tuple): The sequence to be chunked.
        size (int): The size of each chunk.

    Returns:
        list: A list of chunks, where each chunk is a sublist containing elements
              from the original sequence, divided based on the specified size.
    """
    return [seq[i::size] for i in range(size)]



def get_items_chunks(source_path, number_of_threads):
    """
    Retrieves and divides relative paths of items in a folder into chunks for concurrent processing.

    Args:
        source_folder (Path): Path to the source folder containing items.
        number_of_threads (int): Number of chunks (and thus threads) to divide the items into.

    Returns:
        list: A list of chunks, where each chunk is a sublist containing relative paths
              of items from the source folder, divided based on the specified number of threads.
    """
    source_contents = source_path.glob('**/*')
    source_relative_paths = [item.relative_to(source_path).as_posix() for item in source_contents]

    if number_of_threads == 1:
        return source_relative_paths
    else:
        return chunk_list(source_relative_paths, number_of_threads)
    