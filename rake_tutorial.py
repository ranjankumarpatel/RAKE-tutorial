from __future__ import absolute_import
from __future__ import print_function
import six
__author__ = 'a_medelyan'

import rake
import operator
import io

# EXAMPLE ONE - SIMPLE
stoppath = "SmartStoplist.txt"

# 1. initialize RAKE by providing a path to a stopwords file
rake_object = rake.Rake(stoppath, 5, 3, 4)

# 2. run on RAKE on a given text
# sample_file = io.open("data/docs/fao_test/w2167e.txt", 'r',encoding="iso-8859-1")
# text = sample_file.read()
#
# keywords = rake_object.run(text)
#
# 3. print results
# print("Keywords:", keywords)

print("----------")
# EXAMPLE TWO - BEHIND THE SCENES (from https://github.com/aneesha/RAKE/rake.py)

# 1. initialize RAKE by providing a path to a stopwords file
rake_object = rake.Rake(stoppath)

import pandas as pd
import MySQLdb
db = MySQLdb.connect("thinkprodmysql.cpqeziuyg4wm.us-west-2.rds.amazonaws.com", "dbview", "dbview@13972684",
                         "max_engage_v2")
db.autocommit = False

df = pd.read_sql_query(sql="""
SELECT survey_v1_user_response_store.FIELD_VALUE,
       survey_v1_user_response_store.COMMENT
FROM max_engage_v2.survey_v1_user_response_store
     JOIN survey_v1_user_servey_def
        ON survey_v1_user_servey_def.USD_ID =
           survey_v1_user_response_store.USER_SURVEY_DEF_ID
WHERE     survey_v1_user_servey_def.SURVEY_DEF_ID = 21
      AND survey_v1_user_response_store.FIELD_VALUE IS NOT NULL;
""",con=db)
df = df[~df.FIELD_VALUE.isin(['',' ',',','NA','NO','.','..','...','.....','\n','\r\n','1','2','n'])]

text = "\n".join(df.FIELD_VALUE.values)
print(text)

# text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility " \
#        "of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. " \
#        "Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating"\
#        " sets of solutions for all types of systems are given. These criteria and the corresponding algorithms " \
#        "for constructing a minimal supporting set of solutions can be used in solving all the considered types of " \
#        "systems and systems of mixed types."



# 1. Split text into sentences
sentenceList = rake.split_sentences(text)

for sentence in sentenceList:
    print("Sentence:", sentence)

# generate candidate keywords
stopwordpattern = rake.build_stop_word_regex(stoppath)
phraseList = rake.generate_candidate_keywords(sentenceList, stopwordpattern,rake.load_stop_words(stoppath))
print("Phrases:", phraseList)

# calculate individual word scores
wordscores = rake.calculate_word_scores(phraseList)

# generate candidate keyword scores
keywordcandidates = rake.generate_candidate_keyword_scores(phraseList, wordscores)
for candidate in keywordcandidates.keys():
    print("Candidate: ", candidate, ", score: ", keywordcandidates.get(candidate))

# sort candidates by score to determine top-scoring keywords
sortedKeywords = sorted(six.iteritems(keywordcandidates), key=operator.itemgetter(1), reverse=True)
totalKeywords = len(sortedKeywords)

# for example, you could just take the top third as the final keywords
for keyword in sortedKeywords[0:int(totalKeywords / 3)]:
    print("Keyword: ", keyword[0], ", score: ", keyword[1])

print(rake_object.run(text))

