from django.urls import path, include
from chatapp.views import ThreadView

urlpatterns = [
    path('<str:username>/', ThreadView.as_view())
]