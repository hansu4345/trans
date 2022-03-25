# -*- coding: utf-8 -*-

"""
Definition of views.
"""

import os
import sys
import urllib.request

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
    result_text = request.GET['totaltext']
    return render(request, 'app/result.html', 
        {
            'total_text': result_text
        }
    ) 

