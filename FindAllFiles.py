import os

def find_all_files(folder_path, ending='.wav'):

    """
    Find all files in a given folder with a specified file extension.

    This function searches the specified folder for files that end with
    the given extension (by default '.wav') and returns their filenames
    as a list.

    Parameters
    ----------
    folder_path : str
        Path to the folder in which to search for files.
    ending : str, optional
        File extension to look for. The default is '.wav'.

    Returns
    -------
    list of str
        A list containing the filenames that match the specified file
        extension. If the folder does not exist, an empty list is returned.

    Author: Ludmila Himmelspach
    License: MIT
    """

    all_files = []

    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return all_files

    # Iterate over all (mp4) files in the folder
    for file in os.listdir(folder_path):
        if file.lower().endswith(ending):
            all_files.append(file)

    return all_files