# -*- coding: utf-8 -*-

"""
Definition of views.
"""

import os
import sys
import urllib.request
import json

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    chat = '안녕하세요'
    name = '사용자님'

    return render(request, 'app/index.html',
        {
            'user_chat':chat,
            'user_name':name,
        }
    )

def result(request):
    input_text = request.GET['totaltext'] #문장변수1
    input_source = request.GET['source']
    input_target = request.GET['target']
    #input_source = request.GET['source'] #원본언어변수
    #input_target = request.GET['target'] #도착언어변수

    #파파고 문장변수2
    papago_json_2 = papago(input_text,input_source,input_target)
    papago_jsonObject_2 = json.loads(papago_json_2)
    papago_result_2 = papago_jsonObject_2.get("message").get("result").get("translatedText")
    #파파고 문장변수3 (역번역)
    papago_json_3 = papago(papago_result_2,input_target,input_source)
    papago_jsonObject_3 = json.loads(papago_json_3)
    papago_result_3 = papago_jsonObject_3.get("message").get("result").get("translatedText")

    #이후 input_text와 papago_result_3 일치율 체크


    return render(request, 'app/result.html', 
        {
            'papago': papago_result_2,
            'papago_reverse': papago_result_3
        }
    ) 


def papago(input_text,input_source,input_target):
    papago_input = input_text #번역문장
    papago_source = input_source #원본언어
    papago_target = input_target #목적언어
    client_id = "hyvOklk2orQl2ogIjoPP"
    client_secret = "GS2Up8j18T"
    data = "source=" + papago_source + "&target=" + papago_target + "&text=" + papago_input 
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

