# -*- coding: utf-8 -*-

"""
Definition of views.
"""

import os
import sys
import urllib.request
import json
import googletrans
import kakaotrans
import numpy as np

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest

from difflib import SequenceMatcher

from numpy import dot
from numpy.linalg import norm
from konlpy.tag import Okt #한국어 형태소 분석
from sklearn.feature_extraction.text import TfidfVectorizer


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    return render(request, 'app/index.html',
        {
            
        }
    )

def result(request):
    input_text = request.GET['totaltext'] #번역할문장
    input_source = request.GET['source'] #원본언어변수
    input_target = request.GET['target'] #도착언어변수

    #파파고 번역된문장(문장변수2)
    papago_json_2 = papago(input_text,input_source,input_target)
    papago_jsonObject_2 = json.loads(papago_json_2)
    papago_result_2 = papago_jsonObject_2.get("message").get("result").get("translatedText")
    #파파고 역번역문장(문장변수3)
    papago_json_3 = papago(papago_result_2,input_target,input_source)
    papago_jsonObject_3 = json.loads(papago_json_3)
    papago_result_3 = papago_jsonObject_3.get("message").get("result").get("translatedText")
   
    #구글 번역된문장(문장변수2)
    google_result_2 = google(input_text,input_source,input_target)
    #구글 역번역문장(문장변수3)
    google_result_3 = google(google_result_2,input_target,input_source)

    #카카오 번역된문장(문장변수2)
    kakao_result_2 = kakao(input_text,input_source,input_target)
    #카카오 역번역문장(문장변수3)
    kakao_result_3 = kakao(kakao_result_2,input_target,input_source)
  

    #이후 input_text(번역할문장)와 *_result_3(역번역문장)의 일치율 체크

    #한 자씩 단순비교, difflib-SequenceMatcher
    match_rate_papago = f'{SequenceMatcher(None, input_text, papago_result_3).ratio()*100:.1f}%'
    match_rate_google = f'{SequenceMatcher(None, input_text, google_result_3).ratio()*100:.1f}%'
    match_rate_kakao = f'{SequenceMatcher(None, input_text, kakao_result_3).ratio()*100:.1f}%'


    #코사인 유사도, 한->영
    if input_source == 'ko':
        okt = Okt()
        v_in = okt.nouns(input_text)
        v_papago = okt.nouns(papago_result_3)
        v_google = okt.nouns(google_result_3)
        v_kakao = okt.nouns(kakao_result_3)

        v_set = v_in + v_papago + v_google + v_kakao
        feats = set(v_set)

        v_in_arr = np.array(make_matrix(feats, v_in))
        v_papago_arr = np.array(make_matrix(feats, v_papago))
        v_google_arr = np.array(make_matrix(feats, v_google))
        v_kakao_arr = np.array(make_matrix(feats, v_kakao))

        cs_papago = cos_sim(v_in_arr, v_papago_arr)
        cs_google = cos_sim(v_in_arr, v_google_arr)
        cs_kakao = cos_sim(v_in_arr, v_kakao_arr)


    #코사인 유사도, 영->한
    elif input_source == 'en':
        doc_list = [input_text, papago_result_3, google_result_3, kakao_result_3]

        tfidf_vect_simple = TfidfVectorizer()
        feature_vect_simple = tfidf_vect_simple.fit_transform(doc_list)
 
        feature_vect_dense = feature_vect_simple.todense()

        vect1 = np.array(feature_vect_dense[0]).reshape(-1,)
        vect2 = np.array(feature_vect_dense[1]).reshape(-1,)
        vect3 = np.array(feature_vect_dense[2]).reshape(-1,)
        vect4 = np.array(feature_vect_dense[3]).reshape(-1,)

        cs_papago = cos_sim(vect1, vect2)
        cs_google = cos_sim(vect1, vect3)
        cs_kakao = cos_sim(vect1, vect4)


    #순위
    if cs_papago >= cs_google and cs_papago > cs_kakao :
        one_name = "파파고 번역"
        one_trans = papago_result_2
        one_reverse = papago_result_3
        if cs_google > cs_kakao :
            two_name = "구글 번역"
            two_trans = google_result_2
            two_reverse = google_result_3
            three_name = "카카오 번역"
            three_trans = kakao_result_2
            three_reverse = kakao_result_3
        else :
            two_name = "카카오 번역"
            two_trans = kakao_result_2
            two_reverse = kakao_result_3
            three_name = "구글 번역"
            three_trans = google_result_2
            three_reverse = google_result_3

    if cs_google > cs_papago and cs_google >= cs_kakao :
        one_name = "구글 번역"
        one_trans = google_result_2
        one_reverse = google_result_3
        if cs_papago > cs_kakao :
            two_name = "파파고 번역"
            two_trans = papago_result_2
            two_reverse = papago_result_3
            three_name = "카카오 번역"
            three_trans = kakao_result_2
            three_reverse = kakao_result_3
        else :
            two_name = "카카오 번역"
            two_trans = kakao_result_2
            two_reverse = kakao_result_3
            three_name = "파파고 번역"
            three_trans = papago_result_2
            three_reverse = papago_result_3

    if cs_kakao >= cs_papago and cs_kakao > cs_google :
        one_name = "카카오 번역"
        one_trans = kakao_result_2
        one_reverse = kakao_result_3
        if cs_papago > cs_google :
            two_name = "파파고 번역"
            two_trans = papago_result_2
            two_reverse = papago_result_3
            three_name = "구글 번역"
            three_trans = google_result_2
            three_reverse = google_result_3
        else :
            two_name = "구글 번역"
            two_trans = google_result_2
            two_reverse = google_result_3
            three_name = "파파고 번역"
            three_trans = papago_result_2
            three_reverse = papago_result_3


    #렌더
    return render(request, 'app/result.html', 
        {
            '1st_name': one_name,
            '1st_trans': one_trans,
            '1st_reverse': one_reverse,
            
            '2nd_name': two_name,
            '2nd_trans': two_trans,
            '2nd_reverse': two_reverse,
            
            '3rd_name': three_name,
            '3rd_trans': three_trans,
            '3rd_reverse': three_reverse,

            'papago': papago_result_2,
            'papago_reverse': papago_result_3,

            'google': google_result_2,
            'google_reverse': google_result_3,

            'kakao': kakao_result_2,
            'kakao_reverse': kakao_result_3,

            'papago_match':match_rate_papago,
            'google_match':match_rate_google,
            'kakao_match':match_rate_kakao,

            'papago_cs':cs_papago,
            'google_cs':cs_google,
            'kakao_cs':cs_kakao,

        }
    ) 


def papago(input_text,input_source,input_target):
    papago_text = input_text #번역문장
    papago_source = input_source #원본언어
    papago_target = input_target #목적언어
    client_id = "hyvOklk2orQl2ogIjoPP"
    client_secret = "GS2Up8j18T"
    data = "source=" + papago_source + "&target=" + papago_target + "&text=" + papago_text
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        papago_output = response_body.decode('utf-8')
    return papago_output

def google(input_text,input_source,input_target):
    google_text = input_text #번역문장
    google_source = input_source #원본언어
    google_target = input_target #목적언어
    google_result = googletrans.Translator().translate(google_text, src=google_source, dest=google_target)
    return google_result.text

def kakao(input_text,input_source,input_target):
    kakao_text = input_text #번역문장
    kakao_source = input_source #원본언어
    kakao_target = input_target #목적언어

    if input_source == 'ko':
        kakao_source = 'kr'
    elif input_source == 'ja':
        kakao_source = 'jp'
    elif input_source == 'zh-CN':
        kakao_source = 'cn'

    if input_target == 'ko':
        kakao_target = 'kr'
    elif input_target == 'ja':
        kakao_target = 'jp'
    elif input_target == 'zh-CN':
        kakao_target = 'cn'

    kakao_result = kakaotrans.Translator().translate(kakao_text, src=kakao_source, tgt=kakao_target)
    return kakao_result

#코사인 유사도를 구하는 함수
def cos_sim(a, b):
    return dot(a, b)/(norm(a)*norm(b))

# 기준이 되는 키워드와 벡터 키워드 리스트를 받아서 키워드별 빈도를 구하는 함수 
def make_matrix(feats, list_data): 
    freq_list = [] 
    for feat in feats: 
        freq = 0 
        for word in list_data:
           if feat == word: 
               freq += 1
        freq_list.append(freq) 
    return freq_list
