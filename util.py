import json
import pandas as pd
import os
import spacy
import json_lines
import matplotlib.pyplot as plt
from urllib import response
from urllib.request import urlopen
import requests
import tarfile
from tqdm import tqdm

nlp = spacy.blank("en")

def word_tokenize(sent):
    doc = nlp(sent)
    return [token.text for token in doc]

def load_json_file(file_path, logging, encoding='utf-8'):
    content = None
    try:
        # with open(file_path, 'r') as f_in:
        # content = json.load(f_in)
        content = json.loads(get_file_contents(file_path, encoding=encoding))
        if logging is not None:
            logging.info('(function {}) is run successfuly and load the file: {}'.format(load_json_file.__name__, file_path))
    except Exception as e:
        if logging is not None:
            logging.error('(function {}) has an error: {}'.format(load_json_file.__name__, e))
        raise
    return content

def load_json_line_file(file_path, logging, encoding='utf-8'):
    content = []
    try:
        with open(file_path, 'r', encoding=encoding) as f:  # opening file in binary(rb) mode
            for item in json_lines.reader(f):
                content.append(item)

        if logging is not None:
            logging.info('(function {}) is run successfuly and load the file: {}'.format(load_json_line_file.__name__, file_path))
    except Exception as e:
        if logging is not None:
            logging.error('(function {}) has an error: {}'.format(load_json_line_file.__name__, e))
        raise
    return content

def create_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

"""
Extract the .tar.gz compressed file using tarfile package
Uses tdqm to display the uncompress progress

file_dest: where the compressed file is
new_path_to_file: where the uncompressed files are saved
"""
def extract_tar_gz_file(file_dest, new_path_to_file):
    # open the tar.gz file
    with tarfile.open(name=file_dest) as tar:
        # Go over each member
        for member in tqdm(iterable=tar.getmembers(), total=len(tar.getmembers()), desc='Extracting'):
            # Extract member
            tar.extract(member=member, path=new_path_to_file)
    # remove the zip file
    print("Deleted the .tar.gz file at %s"%file_dest)
    os.remove(file_dest)


def dump_json_file(file_path, content, logging, encoding='utf-8'):
    try:
        with open(file_path, 'w', encoding=encoding) as f_out:
            json.dump(content, f_out, indent=1)
        if logging is not None:
            logging.info(
                '(function {}) is run successfuly and write the file: {}'.format(dump_json_file.__name__, file_path))
            print('(function {}) is run successfuly and write the file: {}'.format(dump_json_file.__name__, file_path))
    except Exception as e:
        if logging is not None:
            logging.error('(function {}) has an error: {}'.format(dump_json_file.__name__, e))
        raise

def get_file_contents(filename, encoding='utf-8'):
    with open(filename, encoding=encoding) as f:
        content = f.read()
    return content


def get_file_contents_as_list(file_path, encoding='utf-8', ignore_blanks=True):
    contents = get_file_contents(file_path, encoding=encoding)
    lines = contents.split('\n')
    lines = [line for line in lines if line != ''] if ignore_blanks else lines
    return lines

def load_csv_file(file_path, sep, header, logging, names=None, usecols=None):
    content = None
    try:
        with open(file_path, 'r') as f_in:
            content = pd.read_csv(file_path,sep=sep, header=header, names=names, usecols=None)
        if logging is not None:
            logging.info(
                '(function {}) is run successfuly and load the file: {}'.format(load_csv_file.__name__, file_path))
    except Exception as e:
        if logging is not None:
            logging.error('(function {}) has an error: {}'.format(load_csv_file.__name__, e))
        raise
    return content

def parse_source_files(data_path, source_files, logging, item_seperator=',', k_v_seperator=':'):
    source_path = data_path
    _additional_files = dict()
    try:
        for _ in source_files.split(item_seperator):
            _splitted = _.split(k_v_seperator)
            key = _splitted[0].strip()
            value = _splitted[1].strip()
            print("indx:{}, key:{}, value:{}".format(_, key,value))
            if os.path.isfile(os.path.join(source_path, value)) or os.path.isdir(os.path.join(source_path, value)):
                _additional_files[key] = os.path.join(source_path, value)
            else:
                _additional_files[key] = value
        if logging is not None:
            logging.info(
                '(function {}) is run successfuly'.format(parse_source_files.__name__, data_path))
    except Exception as e:
        if logging is not None:
            logging.error('(function {}) has an error: {}'.format(parse_source_files.__name__, e))
        raise
    return _additional_files

"""
Method to get the size (bytes) of a directory (including all of its child directory)
Code taken from:
https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
"""
def get_dir_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    
    return total_size # bytes

"""
Method to convert bytes in int into a a human recognizable size in string
Dynamically change the unit of the size, depending on how big it is
"""
def get_human_readable_size(size, precision=2):
    suffixes= ['B','KB','MB','GB','TB'] # list of unit
    suffixIndex = 0 # currently choosing from B
    while size > 1024:
        suffixIndex += 1 # move up to the next unit
        size = size / 1024.0 # convert the size to the next unit
    result = "%.*f %s"%(precision,size,suffixes[suffixIndex])
    return result

"""
Method to convert from GB to bytes
"""
def get_bytes_from_gigabytes(num_gb):
    to_byte = 1073741824
    return num_gb * to_byte

"""
Method to check if the target directory has enough space for a model
Raise an error if there is not enough space
"""
def check_remaining_space(num_gb, path):
    # calculate the remaining size
    num_bytes = get_bytes_from_gigabytes(num_gb) # 45 GB = # bytes
    statvfs = os.statvfs(path)
    remaining_size = statvfs.f_frsize * statvfs.f_bavail
    if remaining_size < num_bytes:
        raise SystemError("Free space in your directory: %s, space needed: %s"
    %(get_human_readable_size(remaining_size), get_human_readable_size(num_bytes)))