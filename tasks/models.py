from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=200) 
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + " - by " + self.user.username
    

#  EQUIPOS  #

class Team(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    members = models.ManyToManyField(
        User,
        through='TeamMember',
        related_name='teams'
    )
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class TeamMember(models.Model):
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"

#  TORNEOS  #
class Tournament(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tournaments/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class TournamentTeam(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tournament', 'team')

    def __str__(self):
        return f"{self.team.name} - {self.tournament.name}"
    

#  ARBITROS  #
class Referee(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='referees'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('tournament', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.tournament.name}"
    
#  PARTIDOS  #
class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    home_team = models.ForeignKey(
        Team,
        related_name='home_matches',
        on_delete=models.CASCADE
    )
    away_team = models.ForeignKey(
        Team,
        related_name='away_matches',
        on_delete=models.CASCADE
    )


    round_number = models.PositiveIntegerField()

  
    home_goals = models.IntegerField(null=True, blank=True)
    away_goals = models.IntegerField(null=True, blank=True)

    played = models.BooleanField(default=False)

    scheduled_date = models.DateField(
        null=True,
        blank=True
    )

    scheduled_time = models.TimeField(
        null=True,
        blank=True
    )

    field_name = models.CharField(
        max_length=200,
        blank=True
    )

    location_url = models.URLField(
        blank=True
    )

    referee = models.ForeignKey(
        Referee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"J{self.round_number}: {self.home_team.name} vs {self.away_team.name}"
