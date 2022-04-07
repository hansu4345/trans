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

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    chat = '안녕하세요'

    return render(request, 'app/index.html',
        {
            'user_chat':chat,
        }
    )

def result(request):
    input_text = request.GET['totaltext'] #번역할문장
    input_source = request.GET['source']
    input_target = request.GET['target']
    #input_source = request.GET['source'] #원본언어변수
    #input_target = request.GET['target'] #도착언어변수

    #파파고 번역된문장(문장변수2)
    papago_json_2 = papago(input_text,input_source,input_target)
    papago_jsonObject_2 = json.loads(papago_json_2)
    papago_result_2 = papago_jsonObject_2.get("message").get("result").get("translatedText")
    #파파고 역번역문장(문장변수3)
    papago_json_3 = papago(papago_result_2,input_target,input_source)
    papago_jsonObject_3 = json.loads(papago_json_3)
    papago_result_3 = papago_jsonObject_3.get("message").get("result").get("translatedText")

    #이후 input_text와 papago_result_3 일치율 체크

   
    #구글 번역된문장(문장변수2)
    google_result_2 = google(input_text,input_source,input_target)
    #구글 역번역문장(문장변수3)
    google_result_3 = google(google_result_2,input_target,input_source)


    #카카오 번역된문장(문장변수2)
    kakao_result_2 = kakao(input_text,input_source,input_target)
    #카카오 역번역문장(문장변수3)
    kakao_result_3 = kakao(kakao_result_2,input_target,input_source)


    return render(request, 'app/result.html', 
        {
            'papago': papago_result_2,
            'papago_reverse': papago_result_3,

            'google': google_result_2,
            'google_reverse': google_result_3,

            'kakao': kakao_result_2,
            'kakao_reverse': kakao_result_3,
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