# -*- coding: utf-8 -*-

# logging 관련
from logging.config import dictConfig
import logging

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(message)s',
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['file']
    }
})

# 필요 모듈 import
import konlpy
import numpy as np
import pandas as pd
from konlpy.tag import Okt

import regex as re

okt = Okt()

import pickle
import ast

"""##### 사용할 데이터 로드"""

# entity 데이터 로드
data = np.load('./museumbot/entity.npy', allow_pickle=True)
entity_data_modi = pd.DataFrame(data)

# intent 데이터 로드 후 결측치 변환
intent_data = pd.read_csv('./museumbot/intent.csv')
intent_data = intent_data.iloc[:, 1:]
intent_data = intent_data.fillna(' ')
for i in range(len(intent_data)):  # 정규식을 이용한 특수문자 제거
    for j in range(len(intent_data.columns)):
        intent_data.iloc[i, j] = intent_data.iloc[i, j].replace("'", '').replace(")", '').replace("(", '').replace(",",
                                                                                                                   '')

# QA 데이터 로드
with open('./museumbot/QA_pair.pickle', 'rb') as handle:
    QA = pickle.load(handle)

"""# 데이터 preprocess

##### intent data 전처리
"""


# data 형태소 추출 후 원본 data에 합쳐주는 함수
def data_generate(columns_name):
    colum_list = intent_data[columns_name].tolist()
    a = []
    for i in colum_list:
        if i != " ":
            a.append(okt.morphs(i))
        else:
            a.append('')
    df = pd.Series(a, name=columns_name + "_변환")
    df = pd.concat([intent_data, df], axis=1)
    return df


# data 처리
a = list(intent_data.columns)

for i in a:
    intent_data = data_generate(i)

# 대표 개체명 추출
intent_data_ner = intent_data.iloc[:, 0]

# 데이터셋 생성
intent_data_modi = intent_data.iloc[:, 105:]
intent_data_modi = pd.concat([intent_data_ner, intent_data_modi], axis=1)

"""# 답변 출력 함수

##### entity 추출
"""

# entity 추출 함수
final_entity = []  # 말 그대로 최종 entity
# a = []  # QA_pair에 넘겨주는 부분(전체 set - entity set)
error_check = []  # entity와 intent의 error check list


def entity_extract(input, final_entity):
    # 필요한 리스트 만들기
    pos_entity = []
    pos_index = []

    # input을 형태소 처리 후 집합으로 변경
    morp_input = set(okt.morphs(input))

    # 형태소 처리된 entity data 값을 한개씩 불러와서, 처리된 input 값과 겹치는 부분(=result)만 골라내기
    # morp_input = 형태소 처리된 input 값
    # morp_dataset = 형태소 처리된 entity DB
    # result = morp_input, morp_dataset의 교집합
    for i in range(len(entity_data_modi)):
        for j in range(len(entity_data_modi.columns)):
            morp_dataset = set(entity_data_modi.iloc[i, j])
            result = morp_dataset & morp_input

            # result와 morp_dataset의 교집합의 원소가 하나 이상이고 데이터와 일치하는 경우 pos_entity list에 추가, 그리고 그 경우에 i값(=데이터의 index 값)을 pos_index list에 추가
            if len(result) != 0 and result == morp_dataset:
                pos_entity.append(result)
                pos_index.append(i)

    # 가장 많이 겹치는 부분의 인덱스를 불러옴
    # 예외처리 : 만약 겹치는 부분이 없다면, 이전의 인덱스를 불러옴
    try:
        a = []
        entity_index = pos_index[np.argmax(pos_entity)]

        # 대표 entity 출력
        entity = entity_data_modi.iloc[entity_index, 0]
        error_check.append("1")
        final_entity.clear()
        final_entity.append(entity)
        a.append(morp_input - np.max(pos_entity))
        print(morp_input)
        print(np.max(pos_entity))
        return a[0]

    except:
        a = set(okt.morphs(input))
        return a


"""##### intent 추출"""

# intent 추출 함수
final_intent = []
final_intent_f = []
morp_dataset_f = []
morp_input_f = []


def intent_extract1(a):
    # 필요한 리스트 만들기
    pos_intent = []
    pos_index = []

    # 형태소 처리된 intent data 값을 한개씩 불러와서, 처리된 input 값과 겹치는 부분(=result)만 골라내기
    # morp_dataset = 형태소 처리된 intent DB
    # result = morp_input, morp_dataset의 교집합
    mean = intent_data_modi.iloc[4, 1:].tolist()

    for i in range(len(mean)):
        morp_dataset = set(mean[i])
        result = morp_dataset & a

        # result와 morp_dataset의 교집합의 원소가 하나 이상이고 데이터와 일치하는 경우 pos_intent list에 추가, 그리고 그 경우에 i값(=데이터의 index 값)을 pos_index list에 추가
        if len(result) != 0 and result == morp_dataset:
            pos_intent.append(result) # 인텐트가 들어감
            pos_index.append(i)


    # a가 가장 많이 겹치는 부분의 인덱스를 불러옴
    # 예외처리 : 만약 겹치는 부분이 없다면, 이전의 인덱스를 불러옴
    try:
        b = []
        b.append(a - np.max(pos_intent))
        b = b[0]
        
        return b

    except:
        b = a
        
        return b


def intent_extract2(b, final_intent):
    # 필요한 리스트 만들기
    pos_intent = []
    pos_index = []

    # 형태소 처리된 intent data 값을 한개씩 불러와서, 처리된 input 값과 겹치는 부분(=result)만 골라내기
    # morp_dataset = 형태소 처리된 intent DB
    # result = morp_input, morp_dataset의 교집합
    for i in range(len(intent_data_modi)):
        for j in range(len(intent_data_modi.columns)):
            morp_dataset = set(intent_data_modi.iloc[i, j])
            result = morp_dataset & b

            # result와 morp_dataset의 교집합의 원소가 하나 이상이고 데이터와 일치하는 경우 pos_intent list에 추가, 그리고 그 경우에 i값(=데이터의 index 값)을 pos_index list에 추가
            if len(result) != 0 and result == morp_dataset:
                pos_intent.append(result)
                pos_index.append(i)
    
    if len(pos_intent) == 0:
        pos_intent.append({'어떤', '뜻'})
        pos_index.append(4)


    # a가 가장 많이 겹치는 부분의 인덱스를 불러옴
    # 예외처리 : 만약 겹치는 부분이 없다면, 이전의 인덱스를 불러옴
    try:
        intent_index = pos_index[np.argmax(pos_intent)]

        # 대표 intent 출력
        intent = intent_data_modi.iloc[intent_index, 0]
        error_check.append("1")
        final_intent.clear()
        final_intent.append(intent)

        # 변수를 list에 담아준다.
        morp_dataset_f.append(morp_dataset)
        morp_dataset.append()

        return final_intent

    except:
        return final_intent




"""##### Q&A 매칭 함수"""


def QA_pair(final_entity, final_intent):
    key = final_entity + ' ' + final_intent
    imgs = []
    try:
        if str(QA[key]) == '0':
            return "DB에 있음", "준비된 답변이 없네요.", imgs
        else:
            result = QA[key]
            if "\t" in result:
                answer, imgs = QA[key].split('/t')
                imgs = ast.literal_eval(imgs)
            else:
                answer = result
            return "DB에 있음", answer, imgs
    except:
        return "entity는 있으나 그에 맞는 intent가 없음", "조금 더 자세히 질문해주실래요?", imgs


# 챗봇 실행
def search_answer_from_bot(req, final_entity, final_intent):
    try:
        imgs=[]
        final_intent = intent_extract2(intent_extract1(entity_extract(req, final_entity)), final_intent)
        # print(a)
        # print(error_check)
        # print(final_entity[0])
        # print(final_intent[0])
        if len(error_check) == 0:
            res0 = 'entity와 intent 모두 DB에 없음'
            res1 = "좀 더 다르게 질문해보실래요?"
        else:
            if QA_pair(final_entity[0], final_intent[0]) == 0:
                res0 = 'DB에 아예 없음'
                res1 = "그건 제가 모르는 분야네요. 다음 번엔 꼭 알려드릴게요!"
            else:
                res0, res1, imgs = QA_pair(final_entity[0], final_intent[0])
        return res0, res1, imgs, final_entity, final_intent
    except:
        res0 = '예외 발생'
        res1 = '제가 답변드릴 수 있는 것이 아니네요. T.T 다른 궁금한 건 없으신가요?'
    error_check.clear()
    return res0, res1, [], final_entity, final_intent
