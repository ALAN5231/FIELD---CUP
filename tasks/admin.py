from django.contrib import admin
from .models import Task, Team, Tournament, TournamentTeam, Match


class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'datecompleted')

# Register your models here.
admin.site.register(Task, TaskAdmin) 

admin.site.register(Team)
admin.site.register(Tournament)
admin.site.register(TournamentTeam)
admin.site.register(Match)