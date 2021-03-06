# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
# Script created by Dallin Christensen Thursday March 4th, 2021

"""
Purpose
Perform syntax analysis on French phrases to convert them to inverted questions

"""

import logging
from pprint import pprint
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

partsOfSpeech = ['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET',
                 'INTJ', 'NOUN', 'NUM', 'O', 'PART', 'PRON',
                 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB']

TestPhrasePunct = [{'TokenId': 1, 'Text': 'Tu', 'BeginOffset': 0, 'EndOffset': 2,
                    'PartOfSpeech': {'Tag': 'PRON', 'Score': 0.9997075200080872}},
                   {'TokenId': 2, 'Text': 'aime', 'BeginOffset': 3, 'EndOffset': 7,
                    'PartOfSpeech': {'Tag': 'VERB', 'Score': 0.9982920289039612}},
                   {'TokenId': 3, 'Text': 'aller', 'BeginOffset': 8, 'EndOffset': 13,
                    'PartOfSpeech': {'Tag': 'VERB', 'Score': 0.9991148114204407}},
                   {'TokenId': 4, 'Text': 'au', 'BeginOffset': 14, 'EndOffset': 16,
                    'PartOfSpeech': {'Tag': 'ADP', 'Score': 0.9997463822364807}},
                   {'TokenId': 5, 'Text': 'magasin', 'BeginOffset': 17, 'EndOffset': 24,
                    'PartOfSpeech': {'Tag': 'NOUN', 'Score': 0.9990205764770508}},
                   {'TokenId': 6, 'Text': '?', 'BeginOffset': 24, 'EndOffset': 25,
                    'PartOfSpeech': {'Tag': 'PUNCT', 'Score': 0.9999500513076782}}]
                   # {'TokenId': 7, 'Text': 'Moi', 'BeginOffset': 26, 'EndOffset': 29,
                   #  'PartOfSpeech': {'Tag': 'PRON', 'Score': 0.9687632322311401}},
                   # {'TokenId': 8, 'Text': ',', 'BeginOffset': 29, 'EndOffset': 30,
                   #  'PartOfSpeech': {'Tag': 'PUNCT', 'Score': 0.9999955892562866}},
                   # {'TokenId': 9, 'Text': 'je', 'BeginOffset': 31, 'EndOffset': 33,
                   #  'PartOfSpeech': {'Tag': 'PRON', 'Score': 0.9999996423721313}},
                   # {'TokenId': 10, 'Text': 'veux', 'BeginOffset': 34, 'EndOffset': 38,
                   #  'PartOfSpeech': {'Tag': 'VERB', 'Score': 0.7699386477470398}},
                   # {'TokenId': 11, 'Text': 'te', 'BeginOffset': 39, 'EndOffset': 41,
                   #  'PartOfSpeech': {'Tag': 'PRON', 'Score': 0.9978506565093994}},
                   # {'TokenId': 12, 'Text': 'parler', 'BeginOffset': 42, 'EndOffset': 48,
                   #  'PartOfSpeech': {'Tag': 'VERB', 'Score': 0.9999996423721313}},
                   # {'TokenId': 13, 'Text': '.', 'BeginOffset': 48, 'EndOffset': 49,
                   #  'PartOfSpeech': {'Tag': 'PUNCT', 'Score': 0.999948263168335}}]

TestPhraseWithMultVerbs = [{'TokenId': 1,
                            'Text': 'Je',
                            'BeginOffset': 0,
                            'EndOffset': 2,
                            'PartOfSpeech': {'Tag': 'PRON',
                                             'Score': 0.9999997615814209}
                            },
                           {'TokenId': 2,
                            'Text': 'peux',
                            'BeginOffset': 3,
                            'EndOffset': 7,
                            'PartOfSpeech': {'Tag': 'VERB',
                                             'Score': 0.9804850220680237}
                            },
                           {'TokenId': 3,
                            'Text': 'aller',
                            'BeginOffset': 8,
                            'EndOffset': 13,
                            'PartOfSpeech': {'Tag': 'VERB',
                                             'Score': 0.9998579025268555}
                            },
                           {'TokenId': 4, 'Text': 'au', 'BeginOffset': 14, 'EndOffset': 16,
                            'PartOfSpeech': {'Tag': 'ADP', 'Score': 0.9999063014984131}},
                           {'TokenId': 5, 'Text': 'magasin', 'BeginOffset': 17, 'EndOffset': 24,
                            'PartOfSpeech': {'Tag': 'NOUN', 'Score': 0.9988178610801697}},
                           {'TokenId': 6, 'Text': 'Je', 'BeginOffset': 26, 'EndOffset': 28,
                            'PartOfSpeech': {'Tag': 'PRON', 'Score': 0.9935977458953857}},
                           {'TokenId': 7, 'Text': 'compte', 'BeginOffset': 29, 'EndOffset': 35,
                            'PartOfSpeech': {'Tag': 'VERB', 'Score': 0.9990035891532898}},
                           {'TokenId': 8, 'Text': 'vouloir', 'BeginOffset': 36, 'EndOffset': 43,
                            'PartOfSpeech': {'Tag': 'VERB', 'Score': 0.9990276098251343}},
                           {'TokenId': 9, 'Text': 'faire', 'BeginOffset': 44, 'EndOffset': 49,
                            'PartOfSpeech': {'Tag': 'VERB', 'Score': 0.999724805355072}},
                           {'TokenId': 10, 'Text': 'quelque', 'BeginOffset': 50, 'EndOffset': 57,
                            'PartOfSpeech': {'Tag': 'DET', 'Score': 0.9998217225074768}},
                           {'TokenId': 11, 'Text': 'chose', 'BeginOffset': 58, 'EndOffset': 63,
                            'PartOfSpeech': {'Tag': 'NOUN', 'Score': 0.9996148347854614}}]

TestPhrase = [
    {'TokenId': 1,
     'Text': 'Bonjour',
     'BeginOffset': 0,
     'EndOffset': 7,
     'PartOfSpeech': {'Tag': 'INTJ',
                      'Score': 0.9786997437477112}
     },
    {'TokenId': 2,
     'Text': 'je',
     'BeginOffset': 8,
     'EndOffset': 10,
     'PartOfSpeech': {'Tag': 'PRON',
                      'Score': 1.0}
     },
    {'TokenId': 3,
     'Text': 'suis',
     'BeginOffset': 11,
     'EndOffset': 15,
     'PartOfSpeech': {'Tag': 'AUX',
                      'Score': 0.9963362216949463}
     },
    {'TokenId': 4,
     'Text': 'content',
     'BeginOffset': 16,
     'EndOffset': 23,
     'PartOfSpeech': {'Tag': 'ADJ',
                      'Score': 0.9582428932189941}
     }
]


class ComprehendDetect:
    """Encapsulates Comprehend detection functions."""

    def __init__(self, comprehend_client):
        """
        :param comprehend_client: A Boto3 Comprehend client.
        """
        self.comprehend_client = comprehend_client

    def detect_syntax(self, text, language_code):
        """
        Detects syntactical elements of a document. Syntax tokens are portions of
        text along with their use as parts of speech, such as nouns, verbs, and
        interjections.

        :param text: The document to inspect.
        :param language_code: The language of the document.
        :return: The list of syntax tokens along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_syntax(
                Text=text, LanguageCode=language_code)
            tokens = response['SyntaxTokens']
            logger.info("Detected %s syntax tokens.", len(tokens))
        except ClientError:
            logger.exception("Couldn't detect syntax.")
            raise
        else:
            return tokens


def usage_demo():
    print('-' * 88)
    print("Welcome to the Amazon Comprehend detection demo!")
    print('-' * 88)

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    comp_detect = ComprehendDetect(boto3.client('comprehend'))
    with open('detect_sample.txt') as sample_file:
        sample_text = sample_file.read()

    print("Detecting syntax elements.")
    # analyze text to find newlines and add question marks
    # change peux to puis
    if sample_text.find('peux'):
        syntax_tokens = comp_detect.detect_syntax(sample_text.replace('peux', 'puis'), 'fr')
    else:
        syntax_tokens = comp_detect.detect_syntax(sample_text, 'fr')
    # if sample_text.find(','):

    # print(syntax_tokens)
    # Syntax_tokens is a dict - the part of speech is a dict within that

    # Use TestPhrase instead of calling the API - this will save some data
    # Make a list of words with Partof speech

    wordWithPart = []
    for index, value in enumerate(syntax_tokens):  # Replace with syntax_tokens/TestPhrase when testing
        wordWithPart.append((value['Text'], value['PartOfSpeech']['Tag']))

    # pprint(TestPhrase)
    # print(wordWithPart[0][0], wordWithPart[0][1])

    # Deal with case. Capitalize first letter - leave proper nouns - lower everything else
    # If there isn't punctuation after each phrase
    verbIndex = []
    pronounIndex = []
    foundVerb = False
    foundPron = False
    for index, each in enumerate(wordWithPart):
        if not foundVerb and each[1] == 'VERB' or each[1] == 'AUX':  # Distinguish between AUX and VERB
            # Need to have multiple cases for AUX and for regular VERB -
            # determine which verbs are AUX - être, avoir, devoir
            foundVerb = True
            verbIndex.append(index)
            # if each[0].upper() == 'PEUX':  # Deal with this later
            #     each[0].update('Puis')
            #
            #     y = list(each)
            #     y[0] = "Puis"
            #     each = tuple(y)

        elif not foundPron and each[1] == 'PRON':
            foundPron = True
            pronounIndex.append(index)
        elif not each[0] == ',' and each[1] == 'PUNCT':
            foundVerb = False
            foundPron = False
    print(wordWithPart)

    # this only works if there are indices for both lists,
    # i.e. doesn't work with proper nouns
    for index, verb in enumerate(verbIndex):
        wordWithPart[verbIndex[index]], wordWithPart[pronounIndex[index]] = wordWithPart[pronounIndex[index]], \
                                                                            wordWithPart[verbIndex[index]]
    stringBuilder = ''
    # print(wordWithPart)
    firstWord = True
    for index, each in enumerate(wordWithPart):
        if not each[0] == '?' and each[1] == 'PUNCT':
            stringBuilder = stringBuilder[:-1]
            if not each[0] == ',':
                stringBuilder += ' ?'
                stringBuilder += '\n'
                firstWord = True
            else:
                stringBuilder += each[0]
                stringBuilder += ' '
        elif each[0] == '?':
            stringBuilder += each[0]
            stringBuilder += '\n'
            firstWord = True
        else:
            if firstWord:
                stringBuilder += each[0][0].upper() + each[0][1:]
                stringBuilder += '-'
                if each[0][-1] == 'a' or each[0][-1] == 'e':
                    stringBuilder += 't-'
                firstWord = False
            else:
                stringBuilder += each[0].lower()
                stringBuilder += ' '
        # if index == pronounIndex:
        #     stringBuilder += '-'
        # # elif not each[0] == ',' and each[1] == 'PUNCT':
        # #     stringBuilder += each[0]
        # # else:
        # #     stringBuilder += ' '
    # stringBuilder += "?"
    print(stringBuilder)
    print("Thanks for watching!")
    print('-' * 88)


if __name__ == '__main__':
    usage_demo()
