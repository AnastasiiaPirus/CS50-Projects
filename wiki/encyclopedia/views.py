

from distutils import text_file
from distutils.log import error
from msilib.schema import ListView
import re
from tkinter.filedialog import SaveAs
from turtle import title
from urllib.request import Request
from django.shortcuts import render
from django.http import HttpResponse
from . import util

import markdown2
import random
from urllib.request import urlopen
from django.shortcuts import redirect



def index(request):
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        

    })



def openpage(request, entry):
    entries = util.list_entries()
    try:
        
        return render(request, "encyclopedia/entry.html", {
            "testtext": markdown2.markdown(util.get_entry(entry)),
            "entry": entry,
            
        })
    except:
        return render(request, "encyclopedia/error.html", {
            "randomint":random.choice(entries)
        })


def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        entries = util.list_entries()
        filtered_list = []
        for entry in entries:
            if entry.lower() == searched.lower().strip():
                return render(request, "encyclopedia/entry.html", {
                    "testtext": markdown2.markdown(util.get_entry(entry)),
                    "entry": entry,
                })
            elif searched.lower().strip() in entry.lower():
                filtered_list.append(entry)

        return render(request, "encyclopedia/search.html", {
            'searched': searched,
            'filtered_list': filtered_list

        })

    else:
        return render(request, "encyclopedia/search.html", {

        })


def create(request):

    if request.method == "POST":
        content = request.POST['create']
        title = request.POST['title']
        entries = util.list_entries()
        error = False
        for entry in entries:
            if title.lower().strip() == entry.lower() or title == "":
                error = True
        if error == False:
            util.save_entry(title, content)

            
            return redirect ('/wiki/' +title)
        

        else:
            return render(request, "encyclopedia/create.html", {
                'content': content,
                'error': error,
            })

    else:
        return render(request, "encyclopedia/create.html", {})


def edit(request,entry):
    
    if request.method == "POST":
        content = request.POST['edit']
        title = request.POST['title']
        
        error = False
        if title == "":
            error = True
        if error == False:
            util.save_entry(title, content)
            
            return redirect ('/wiki/' +title)

    
    return render(request, "encyclopedia/edit.html", {
            "testtext": markdown2.markdown(util.get_entry(entry)),
            "entry": entry,
            'text':util.get_entry(entry),
            "randomint":random.choice(util.list_entries())
        })


def randompage(randname):
        randname = random.choice(util.list_entries())
        return redirect(('/wiki/' +randname))