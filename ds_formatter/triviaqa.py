import random
from threading import local
from tqdm import tqdm
import nltk
sent_tokenize = nltk.data.load("tokenizers/punkt/english.pickle")
import sys
import os
import platform
import requests
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import util as UTIL

"""
Check to see if there is a directory './datasets/triviaqa-rc/'
"""
def download_dataset_if_needed():
    path_dir = './datasets/triviaqa-rc'
    if not os.path.exists(path_dir):
        download_triviaqa('./datasets/')
    # Check if the folder has more than 3 GB of data
    elif UTIL.get_dir_size(path_dir) < UTIL.get_bytes_from_gigabytes(1):
        print("Deleted all content in %s"%path_dir)
        # delete all files in the directory
        for file in os.scandir(path_dir):
            os.remove(file.path)
        download_triviaqa('./datasets/')
    else:
        print('TriviaQA-rc has already been downloaded.')

"""
Download the dataset triviaqa.

path: The destination path to save the compressed and uncompressed files
"""
def download_triviaqa(path):
    # check if the input path exists
    if not os.path.exists(path):
        raise Exception("The input path does not exist. Please create it before\
                        calling the method.")
    
    _URL = 'https://nlp.cs.washington.edu/triviaqa/data/triviaqa-rc.tar.gz'
    # get the name of the file from website
    _name = _URL.split('/')[-1]
    # remove extension
    # only get the name before the extension (cons: file.name.tar.gz = file)
    stripped_name = _name[:_name.index('.')]

    # combine the original path with the stripped name (w/o extension) of the dataset
    new_path_to_file = path + stripped_name
    if not os.path.exists(new_path_to_file):
      # create a new directory
        os.makedirs(new_path_to_file)

    # check if the directory has enough space
    UTIL.check_remaining_space(num_gb=7, path=new_path_to_file)

    # retrieve and extract the compressed file
    response = requests.get(_URL, stream = True)
    # utilize tqdm to display the progress of downloading
    file_size = int(response.headers['Content-Length'])
    chunk = 1
    chunk_size = 1024 * 1024
    num_bars = int(file_size / chunk_size)

    desc = "Downloading " + _name
    file_dest = new_path_to_file + '/' + _name # where to write the file to

    # Downloading the file
    with open(file_dest, 'wb') as fp:
        for chunk in tqdm(
                            response.iter_content(chunk_size=chunk_size)
                            , total= num_bars
                            , unit='MB'
                            , desc=desc
                            , leave=True # progressbar stays
                        ):
            fp.write(chunk)
    
    # Extract depending on the model
    UTIL.extract_tar_gz_file(file_dest=file_dest, new_path_to_file=new_path_to_file)
    
    # size of the generated folder
    size = UTIL.get_human_readable_size(UTIL.get_dir_size(new_path_to_file))
    print("\nFinished downloading. Size of the %s directory: %s"%(new_path_to_file, size))

def convert_to_squad_format(qa_content, wikipedia_dir, web_dir, sample_size, seed, max_num_of_tokens):
    qa_json = read_triviaqa_data(qa_content)
    qad_triples = get_qad_triples(qa_json)

    random.seed(int(seed))
    random.shuffle(qad_triples)

    data = []
    for qad in tqdm(qad_triples):
        qid = qad['QuestionId']

        text = get_text(qad, qad['Source'], web_dir, wikipedia_dir)
        selected_text = select_relevant_portion(text, int(max_num_of_tokens))

        question = qad['Question']
        para = {'context': selected_text, 'qas': [{'question': question, 'answers': []}]}
        data.append({'paragraphs': [para]})
        qa = para['qas'][0]
        qa['id'] = get_question_doc_string(qid, qad['Filename'])
        qa['qid'] = qid

        ans_string, index = answer_index_in_document(qad['Answer'], selected_text)
        if index == -1:
            if qa_json['Split'] == 'train':
                continue
        else:
            qa['answers'].append({'text': ans_string, 'answer_start': index})

        if qa_json['Split'] == 'train' and len(data) >= int(sample_size) and qa_json['Domain'] == 'Web':
            break

    squad = {'data': data, 'version': qa_json['Version']}
    return squad


def read_triviaqa_data(trivia_content):
    data = trivia_content #UTIL.load_json_file(file_path=qajson, logging=None)
    # read only documents and questions that are a part of clean data set
    if data['VerifiedEval']:
        clean_data = []
        for datum in data['Data']:
            if datum['QuestionPartOfVerifiedEval']:
                if data['Domain'] == 'Web':
                    datum = read_clean_part(datum)
                clean_data.append(datum)
        data['Data'] = clean_data
    return data

def read_clean_part(datum):
    for key in ['EntityPages', 'SearchResults']:
        new_page_list = []
        for page in datum.get(key, []):
            if page['DocPartOfVerifiedEval']:
                new_page_list.append(page)
        datum[key] = new_page_list
    assert len(datum['EntityPages']) + len(datum['SearchResults']) > 0
    return datum

# Key for wikipedia eval is question-id. Key for web eval is the (question_id, filename) tuple
def get_key_to_ground_truth(data):
    if data['Domain'] == 'Wikipedia':
        return {datum['QuestionId']: datum['Answer'] for datum in data['Data']}
    else:
        return get_qd_to_answer(data)


def get_question_doc_string(qid, doc_name):
    return '{}--{}'.format(qid, doc_name)

def get_qd_to_answer(data):
    key_to_answer = {}
    for datum in data['Data']:
        for page in datum.get('EntityPages', []) + datum.get('SearchResults', []):
            qd_tuple = get_question_doc_string(datum['QuestionId'], page['Filename'])
            key_to_answer[qd_tuple] = datum['Answer']
    return key_to_answer

def answer_index_in_document(answer, document):
    answer_list = answer['NormalizedAliases']
    for answer_string_in_doc in answer_list:
        index = document.lower().find(answer_string_in_doc)
        if index != -1:
            return answer_string_in_doc, index
    return answer['NormalizedValue'], -1

def get_text(qad, domain, web_dir, wikipedia_dir):
    try:
        # Sometimes the windows machine is weird and edit to different name
        if platform.system() == 'Windows':
            temp_name = re.sub('[\/:"*?<>|]', '', qad['Filename'])
            
        local_file = os.path.join(web_dir, temp_name) if domain == 'SearchResults' else os.path.join(wikipedia_dir, temp_name)
        if not os.path.exists(local_file):
            raise Exception(os.path.abspath(local_file))
        file_content = UTIL.get_file_contents(local_file, encoding='utf-8')
    except Exception:
        # Edit the file name since Windows cannot have certain characters on a file
        if platform.system() == 'Windows':
            temp_name = re.sub('[\/:"*?<>|]', '_', qad['Filename'])
        local_file = os.path.join(web_dir, temp_name) if domain == 'SearchResults' else os.path.join(wikipedia_dir, temp_name)
        if not os.path.exists(local_file):
            raise Exception(os.path.abspath(local_file))
        file_content = UTIL.get_file_contents(local_file, encoding='utf-8')
    
    return file_content


def select_relevant_portion(text, max_num_tokens):
    paras = text.split('\n')
    selected = []
    done = False
    for para in paras:
        sents = sent_tokenize.tokenize(para)
        for sent in sents:
            words = nltk.word_tokenize(sent)
            for word in words:
                selected.append(word)
                if len(selected) >= max_num_tokens:
                    done = True
                    break
            if done:
                break
        if done:
            break
        selected.append('\n')
    st = ' '.join(selected).strip()
    return st


def add_triple_data(datum, page, domain):
    qad = {'Source': domain}
    for key in ['QuestionId', 'Question', 'Answer']:
        qad[key] = datum[key]
    for key in page:
        qad[key] = page[key]
    return qad


def get_qad_triples(data):
    qad_triples = []
    for datum in data['Data']:
        for key in ['EntityPages', 'SearchResults']:
            for page in datum.get(key, []):
                qad = add_triple_data(datum, page, key)
                qad_triples.append(qad)
    return qad_triples