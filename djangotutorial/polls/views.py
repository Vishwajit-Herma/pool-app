from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import QuestionForm
from .models import Choice, Question


def is_admin(user):
    return user.is_staff

#
def home(request):
    return redirect("polls:index")


class IndexView(LoginRequiredMixin,generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]
    

class DetailView(LoginRequiredMixin,generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(LoginRequiredMixin,generic.DetailView):
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.choice_set.count() < 2:#
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "This poll is not valid for voting.",
            },
        )

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(
            reverse("polls:results", args=(question.id,))
        )
        # return redirect("polls:results", question.id)

        


@login_required
@user_passes_test(is_admin)
def add_question(request):
    error_message = None

    if request.method == "POST": #
        question_form = QuestionForm(request.POST)

        # Get raw choices
        raw_choices = [
            request.POST.get("choice1"),
            request.POST.get("choice2"),
            request.POST.get("choice3"),
        ]

        # Clean choices: remove empty & whitespace-only values
        choices = [c.strip() for c in raw_choices if c and c.strip()]

        # ---- VALIDATIONS ----
        if not question_form.is_valid():
            error_message = "Please enter a valid question."

        elif len(choices) < 2:
            error_message = "A question must have at least two choices."

        else:
            # Save question
            question = question_form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()

            # Save choices
            for choice_text in choices:
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text
                )

            return redirect("polls:index")

    else:
        question_form = QuestionForm()

    return render(request, "polls/add_question.html", {
        "question_form": question_form,
        "error_message": error_message
    })

def register(request):
    if request.user.is_authenticated:
        return redirect("polls:index")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   
            return redirect("polls:index")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})



# from django.views.generic.edit import FormView
# class RegisterView(FormView):
#     template_name = "registration/register.html"
#     form_class = UserCreationForm
#     success_url = "/polls/"
#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)
#         return super().form_valid(form)
#     def get(self, request, *args, **kwargs):
#         if self.request.user.is_authenticated:
#             return redirect("polls:index")
#         return super().get(request, *args, **kwargs)

# cbv version of register view

# from django.views import View
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import login
# from django.shortcuts import render, redirect   
# class RegisterView(View):
#     def get(self, request):
#         form = UserCreationForm()
#         return render(request, "registration/register.html", {"form": form})

#     def post(self, request):
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect("polls:index")
#         return render(request, "registration/register.html", {"form": form})
    
# # cbv version using CreateView(generic.CreateView)
# from django.views import generic
# class RegisterView(generic.CreateView):
#     form_class = UserCreationForm
#     template_name = "registration/register.html"
#     success_url = "/polls/"

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         login(self.request, self.object)
#         return 
   