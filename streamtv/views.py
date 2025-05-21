from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "streamtv/index.html",)

def users(request):
    return render(request, "streamtv/users.html", {
        "users": Registered_User.objects.all()
    })
