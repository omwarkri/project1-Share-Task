# from django.contrib.auth.models import Permission
# from django.contrib.contenttypes.models import ContentType

# # Define permissions for teams
# content_type = ContentType.objects.get_for_model(Team)

# # Example permissions
# Permission.objects.get_or_create(
#     codename="add_task",
#     name="Can add task",
#     content_type=content_type,
# )

# Permission.objects.get_or_create(
#     codename="delete_task",
#     name="Can delete task",
#     content_type=content_type,
# )

# Permission.objects.get_or_create(
#     codename="edit_team",
#     name="Can edit team",
#     content_type=content_type,
# )