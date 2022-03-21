### Note: This is a forked repository. I am editing this based on my need.
1. Fully support TriviaQA (automatically download, read, and write to the JSON-SQuAD format)\


# Dataset Converter for Question-Answering (QA) Tasks 
Dataset Converter for natural language processing tasks such QA(question-answering) Tasks: from one format to other one

#### QA Dataset Paper & Data :

* [SQuAD v1 paper](https://arxiv.org/pdf/1606.05250) | [SQuAD v1 data](https://github.com/rajpurkar/SQuAD-explorer/blob/master/dataset)
* [SQuAD v2 paper](https://arxiv.org/abs/1806.03822) | [SQuAD v2 data](https://github.com/rajpurkar/SQuAD-explorer/blob/master/dataset) (*NOTE: SQuAD v2 should be also compatible with this code [NOT TESTED]*) 
* [QAngaroo paper](https://transacl.org/ojs/index.php/tacl/article/viewFile/1325/299) | [QAngaroo data](http://bit.ly/2m0W32k)
* [MCTest paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/11/MCTest_EMNLP2013.pdf) | [MCTest data](https://github.com/mcobzarenco/mctest/tree/master/data/MCTest)
* [WikiQA_paper](https://aclweb.org/anthology/D15-1237) | [WikiQA_data](https://www.microsoft.com/en-us/download/details.aspx?id=52419)
* [InsuranceQA paper](https://arxiv.org/abs/1508.01585) | [InsuranceQA data v1](https://github.com/shuzi/insuranceQA/tree/master/V1) - [InsuranceQA data v2](https://github.com/shuzi/insuranceQA/tree/master/V2) 
* [MS_MARCO paper](https://arxiv.org/pdf/1611.09268.pdf) | [MS_MARCO data](http://www.msmarco.org/dataset.aspx)
* [WikiMovies](https://arxiv.org/abs/1606.03126)
* [TriviaQA paper](https://arxiv.org/abs/1705.03551) | [TriviaQA data](http://nlp.cs.washington.edu/triviaqa/)
* [Simple Questions](https://arxiv.org/abs/1506.02075)
* [NarrativeQA paper](https://arxiv.org/abs/1712.07040) | [NarrativeQA data](https://github.com/deepmind/narrativeqa)
* [Ubuntu Dialogue Corpus v2.0 paper](https://arxiv.org/abs/1506.08909) | [Ubuntu Dialogue Corpus v2.0 data](https://github.com/rkadlec/ubuntu-ranking-dataset-creator)
* [NewsQA paper](https://arxiv.org/abs/1611.09830) | [NewsQA data](https://datasets.maluuba.com/NewsQA)
* [Quasar data](http://curtis.ml.cmu.edu/datasets/quasar/)
* **MatchZoo** Each line is the raw query and raw document text of a document. The format is "label \t query \t document_txt".  
#### Supported Formats :
Source | Destination | Status
------------ | ------------- | -------------
QAngaroo| SQuAD| **completed**
MCTest| SQuAD| **completed**
WikiQA| SQuAD| **completed**
InsuranceQA v1| SQuAD| **completed**
InsuranceQA v2| SQuAD| **completed**
TriviaQA| SQuAD| **completed**
NarrativeQA| SQuAD| **completed**
MS MARCO| SQuAD| **completed**
MS MARCO v2| SQuAD| **completed**
WikiMovies| SQuAD| *on hold*
Simple Questions| SQuAD| *on hold*
Ubuntu Corpus v2| SQuAD| **completed**
NewsQA| SQuAD| **completed**
SQuAD| MatchZoo| **completed**
Quasar-T| SQuAD| **completed**
Quasar-S| SQuAD| **completed**

#### Example Call :

You can find the sample call for each format type in the ``` executor.py ``` file such as below. 

### For TriviaQA (Train)
```
python executor.py \
--log_path="./log/log.log" \
--data_path="./data/triviaqa/" \
--from_files="source:./datasets/triviaqa-rc/qa/wikipedia-train.json, wikipedia:./datasets/triviaqa-rc/evidence/wikipedia,web:./datasets/triviaqa-rc/evidence/web,seed:10,token_size:2000,sample_size:1000000" \
--from_format="triviaqa" \
--to_format="squad" \
--to_file_name="wikipedia-train-long.json"
```

### For TriviaQA (Validation)
```
python executor.py \
--log_path="./log/log.log" \
--data_path="./data/triviaqa/" \
--from_files="source:./datasets/triviaqa-rc/qa/wikipedia-dev.json, wikipedia:./datasets/triviaqa-rc/evidence/wikipedia,web:./datasets/triviaqa-rc/evidence/web,seed:10,token_size:2000,sample_size:1000000" \
--from_format="triviaqa" \
--to_format="squad" \
--to_file_name="wikipedia-dev-long.json"
```