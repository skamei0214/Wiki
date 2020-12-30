from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.core.files import File
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from random import choice


from . import util

from markdown2 import Markdown
markdowner = Markdown()


class SearchForm(forms.Form):
    search_term = forms.CharField(label="Search Term")

class NewPage(forms.Form):
    page_title = forms.CharField(label="Page Title")
    page_content = forms.CharField(label="Page Content", widget=forms.Textarea(attrs={'style': 'height: 15em;'}))


def index(request):
    # layout(request)
    entries = util.list_entries()
    entries_sorted = sorted(entries, key=str.lower)

    return render(request, "encyclopedia/index.html", {
        "entries": entries_sorted
    })

def test(request):
    return render(request, "encyclopedia/test.html")

def entry(request, title):

    try:
        return render(request, "encyclopedia/entry.html", {
        "entry_title": title,
        "entry_body": markdowner.convert(util.get_entry(title))
        })
    except FileNotFoundError:
        return HttpResponse("Sorry! This page doesn't exist (yet!).")


def layout(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data["search_term"]
            return HttpResponseRedirect(reverse("encyclopedia:results")), search_term
    else: 
        form = SearchForm()
        search_term = "No search term yet"
    return render(request, "encyclopedia/results.html", {
        "form": form,
        "search_term": search_term
    })


def results(request):
    # Make all entries lowercase to make matching case insensitive
    entries = util.list_entries()
    entries = [entry.lower() for entry in entries]

    search_term = layout(request)[1]
    
    # If exact match, go directly to the page
    if search_term.lower() in entries:
        return render(request, "encyclopedia/entry.html", {
            "entry_title": search_term,
            "entry_body": markdowner.convert(util.get_entry(search_term))
        })
    
    # If not an exact match, return list of potential matches
    else:
        # Create list of similar entries
        matches = []

        for entry in util.list_entries():
            if search_term.lower() in entry.lower():
                matches += [entry]

        return render(request, "encyclopedia/results.html", {
            "search_term": search_term,
            "entries": matches,
            "num_matches": len(matches)
        })

# Updated to reflect add() from tasks project
def newpage(request):

    # If form is submitted
    if request.method == "POST":
        formNewPage = NewPage(request.POST)
        
        # If form inputs are valid and page_title is not duplicate of existing entry
        if ((formNewPage.is_valid()) and (not(formNewPage.cleaned_data["page_title"] in util.list_entries()))):
            
                # Save form inputs in variables
                page_title = formNewPage.cleaned_data["page_title"]
                page_content = formNewPage.cleaned_data["page_content"]
                title_content = f"# {page_title}\n<br>{page_content}"

                # Save variables in markdown file
                util.save_entry(page_title, title_content)

                # Send user to index page after successful submission
                return render(request, "encyclopedia/index.html", {
                    "page_title": page_title,
                    "entries": util.list_entries()
                })
        
        # If form inputs are not valid
        else: 
            # Reload page
            return render(request, "encyclopedia/newpage.html", {
                "formNewPage": formNewPage,
                "invalid_title": 1
            })
    
    # If form is being viewed for the first time (request.method == GET)
    return render(request, "encyclopedia/newpage.html", {
        "formNewPage": NewPage()
    })

def randompage(request):

    entries = util.list_entries()
    numEntries = len(entries)
    numRand = choice(range(numEntries))
    title = entries[numRand]

    return render(request, "encyclopedia/entry.html", {
        "entry_title": title,
        "entry_body": markdowner.convert(util.get_entry(title))
        })

def edit(request, edit_title):
    # If form is submitted
    if request.method == "POST":
        formEdit = NewPage(request.POST)
        
        # If form inputs are valid and page_title is not duplicate of existing entry
        if formEdit.is_valid():
            
            # Save form inputs in variables
            page_title = formEdit.cleaned_data["page_title"]
            page_content = formEdit.cleaned_data["page_content"]

            # Save variables in markdown file
            util.save_entry(page_title, page_content)

            # Send user to entry page after successful submission
            return render(request, "encyclopedia/entry.html", {
                "entry_title": page_title,
                "entry_body": markdowner.convert(util.get_entry(page_title))
            })
        
        # If form inputs are not valid
        else:             
            return render(request, "encyclopedia/edit.html", {
                "formEdit": formEdit
            })
    
    # If form is being viewed for the first time (request.method == GET)

    # Display current content in form field
    formEdit = NewPage(initial={
        'page_title': edit_title,
        'page_content': util.get_entry(edit_title)
    })

    return render(request, "encyclopedia/edit.html", {
        "formEdit": formEdit,
        'page_title': edit_title
    })
