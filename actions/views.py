from django.shortcuts import render


def detail(request):

    return render(request, 'actions/action/detail.html')