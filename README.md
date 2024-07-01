# Folder Synchronization Tool

This Python script provides a folder synchronization tool that synchronizes files and directories from a source folder to a replica folder, using multi-threading for efficient operation. It also includes functionality to clean up the replica folder by deleting items that no longer exist in the source.

## Features

- **Multi-threaded Synchronization:** Utilizes Python's threading module to synchronize folders concurrently, optimizing performance especially for large datasets.
- **Checksum Validation:** Ensures synchronization accuracy by comparing MD5 checksums of files before replication.
- **Logging:** Comprehensive logging setup with both console and file handlers for detailed runtime information.
- **Automatic Folder Creation and Deletion:** Automatically creates folders in the replica directory if they don't exist and deletes items from the replica that are no longer present in the source.

### Running the Script

To synchronize folders, run the script `main.py` with the following command:

```bash
python main.py <source_folder> <replica_folder> <sync_interval> <log_file>
```

## Configuration

### Adjusting Number of Threads

By default, the script determines the number of threads based on the available CPUs (`cpu_count()`). You can modify this setting in `main.py` to optimize synchronization performance based on your system's capabilities.

Example in `main.py`:

```python
number_of_threads = cpu_count()
```