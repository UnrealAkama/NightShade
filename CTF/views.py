from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.generic.detail import DetailView

from CTF.models import Contest, Challenge, Score

from CTF.forms import ChallengeScoreForm



# Create your views here.

@login_required
def current_datetime(request):
    if request.user.is_authenticated():
        return render(request, 'time.html', context_instance=RequestContext(request))


def home_page(request):
    contests = Contest.objects.filter(active=True)
    return render(request, 'home.html', {'contests': contests.iterator()}, context_instance=RequestContext(request), )


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


@login_required
def profile(request):
    return HttpResponseRedirect(reverse('home'))


def ChallengeView(request, slug):
    challenge = get_object_or_404(Challenge,slug=slug,active=True)

    if request.method == 'POST' and not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        kwargs = {'key': challenge.key}
        form = ChallengeScoreForm(request.POST, **kwargs)
        if form.is_valid() and not challenge.solved(request.user):
            score = Score(challenge=challenge, user=request.user, contest=challenge.contest)
            score.save()
            print("Good Flag!")
            messages.add_message(request, messages.SUCCESS, 'Challenge Solved!')
            return HttpResponseRedirect(reverse('challenge-view', args=(slug,)))
        else:
            print("Bad Flag!")
            messages.add_message(request, messages.ERROR, 'That is not the flag!')
    else:
        form = ChallengeScoreForm()

    solved = challenge.solved(request.user)

    return render(request, 'CTF/challenge_detail.html', {'object': challenge, 'form': form, 'solved': solved})


class ContestDetailView(DetailView):
    model = Contest

    def get_context_data(self, **kwargs):
        return super(ContestDetailView, self).get_context_data(**kwargs)
