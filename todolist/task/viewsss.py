from .views.base_views import *
from .views.task_actions import *
from .views.subtask_views import *
from .views.team_views import *
from .views.ai_views import *
from .views.social_views import *
from .views.analytics_views import *
from .views.quiz_views import *
from .views.feeds_views import *

# Landing page view remains here as it's standalone
def landing_page(request):
    return render(request, 'task/landing_page.html')