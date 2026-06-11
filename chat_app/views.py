from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "chat_app/home.html"


class RoomView(TemplateView):
    template_name = "chat_app/room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["room_name"] = self.kwargs["room_name"]
        context["username"] = self.request.GET.get("username")

        return context