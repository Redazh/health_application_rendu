from django.urls import path
from .views import register, login, get_user_profile, google_auth, complete_profile, get_questionnaire, submit_questionnaire,classify_user_view
from .views import send_friend_request, respond_to_friend_request, list_friends, list_pending_requests, remove_friend,suggest_friends,ignore_suggestion, get_fitbit_history, get_recommendation,update_feedback_rating
from .views import list_groups, create_group, add_member, remove_member, delete_group, leave_group, get_group_details, rename_group, fitbit_auth, refresh_fitbit_token, fetch_and_store_fitbit_activity, classify_new_user_view, fetch_and_store_yesterdays_fitbit_activity

urlpatterns = [
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('api/user/profile/', get_user_profile, name='user-profile'),
    path('api/auth/google/', google_auth, name='google-auth'),
    path('api/user/complete-profile/', complete_profile, name='complete-profile'),
    path("api/questionnaire/", get_questionnaire, name="get_questionnaire"),
    path("api/questionnaire/submit/", submit_questionnaire, name="submit_questionnaire"),
    path('api/friends/request/', send_friend_request, name='send_friend_request'),
    path('api/friends/respond/', respond_to_friend_request, name='respond_to_friend_request'),
    path('api/friends/list/', list_friends, name='list_friends'),
    path('api/friends/pending/', list_pending_requests, name='list_pending_requests'),
    path('api/friends/remove/', remove_friend, name='remove_friend'),
    path('api/friends/suggestions/', suggest_friends, name='suggest_friends'),
    path('api/friends/ignore/', ignore_suggestion, name='ignore_suggestion'),
    path("api/groups/list/", list_groups, name="list_groups"),
    path("api/groups/create/", create_group, name="create_group"),
    path("api/groups/add_member/", add_member, name="add_member"),
    path("api/groups/remove_member/", remove_member, name="remove_member"),
    path("api/groups/delete/", delete_group, name="delete_group"),
    path("api/groups/leave/", leave_group, name="leave_group"),
    path("api/groups/<int:group_id>/", get_group_details, name="get_group_details"),  # Récupérer les détails d'un groupe
    path("api/groups/rename/", rename_group, name="rename_group"),
    path('api/auth/fitbit/', fitbit_auth, name='fitbit-auth'),
    path('api/auth/fitbit/refresh/', refresh_fitbit_token, name='fitbit-refresh'),
    path('api/fitbit/activity/', fetch_and_store_fitbit_activity, name='get-steps'),
    path('api/fitbit/classify/', classify_new_user_view, name='new_user'),
    path('api/fitbit/fetch_yesterday/', fetch_and_store_yesterdays_fitbit_activity, name='yesterday'),
    path('api/fitbit/history/', get_fitbit_history, name='get-history'),
    path("api/recommendation/", get_recommendation, name="get_recommendation"),
    path('api/fitbit/classify/', classify_user_view, name='new_user'),
    path("api/update_rating/", update_feedback_rating, name="update_feedback_rating"),
]