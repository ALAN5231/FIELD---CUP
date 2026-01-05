from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm, TournamentForm
from .models import Task, Team, TeamMember, Tournament, TournamentTeam, Match
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from itertools import combinations
from math import ceil
from django.contrib import messages

# Create your views here.

def home(request): #funcion para la pagina de inicio
    return render(request, 'home.html')

def signup(request): #funcion para registrar usuario

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            #REGISTRAR USUARIO
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('lobby')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'Username ya existe'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Passwords do not match'
        })

@login_required 
def signout(request): #funcion para cerrar sesion
    logout(request)
    return redirect('home')

def signin(request):  #funcion para iniciar sesion
    if request.method == 'GET':  
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('lobby')
                
@login_required
def lobby(request):
    teams = Team.objects.filter(
        Q(owner=request.user) |
        Q(teammember__user=request.user)
    ).distinct()

    tournaments = Tournament.objects.filter(
        Q(owner=request.user) |
        Q(tournamentteam__team__teammember__user=request.user)
    ).distinct()

    return render(request, 'lobby.html', {
        'teams': teams,
        'tournaments': tournaments
    })

@login_required
def create_team(request):
    if request.method == 'GET':
        return render(request, 'create_team.html')
    else:
        team = Team.objects.create(
            name=request.POST['name'],
            owner=request.user,
            logo=request.FILES.get('logo')
        )

        # Agregar automáticamente al owner como integrante
        TeamMember.objects.create(
            team=team,
            user=request.user
        )

        return redirect('lobby')



@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # Permiso: owner o integrante
    is_member = TeamMember.objects.filter(
        team=team,
        user=request.user
    ).exists()

    if request.user != team.owner and not is_member:
        return HttpResponseForbidden("No tienes acceso a este equipo")

    members = TeamMember.objects.filter(team=team)

    return render(request, 'team_detail.html', {
        'team': team,
        'members': members
    })

    
@login_required
def edit_team(request, team_id):
    team = get_object_or_404(Team, pk=team_id, owner=request.user)

    if request.method == 'GET':
        return render(request, 'edit_team.html', {
            'team': team
        })
    else:
        team.name = request.POST['name']

        if request.FILES.get('logo'):
            team.logo = request.FILES['logo']

        team.save()
        return redirect('team_detail', team_id=team.id)
    
@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.user != team.owner:
        return HttpResponseForbidden()

    # BLOQUEO SI EL EQUIPO TIENE PARTIDOS
    has_matches = Match.objects.filter(
        home_team=team
    ).exists() or Match.objects.filter(
        away_team=team
    ).exists()

    if has_matches:
        messages.error(
            request,
            "No puedes eliminar este equipo porque ya tiene partidos en un torneo."
        )
        return redirect('team_detail', team_id=team.id)

    team.delete()
    messages.success(request, "Equipo eliminado correctamente.")
    return redirect('lobby')
    
@login_required
def add_team_member(request, team_id):
    team = get_object_or_404(Team, pk=team_id, owner=request.user)
    error = None

    if request.method == 'POST':
        username = request.POST['username']
        user = User.objects.filter(username=username).first()

        if not user:
            error = 'El usuario no existe.'
        else:
            TeamMember.objects.get_or_create(
                team=team,
                user=user
            )
            return redirect('team_detail', team_id=team.id)

    return render(request, 'add_team_member.html', {
        'team': team,
        'error': error
    })
    
@login_required
def remove_team_member(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)

    # Solo el owner puede eliminar integrantes
    if request.user != team.owner:
        return HttpResponseForbidden("No tienes permiso para esta acción")

    # El owner NO puede eliminarse a sí mismo
    if user_id == team.owner.id:
        return redirect('team_detail', team_id=team.id)

    member = get_object_or_404(
        TeamMember,
        team=team,
        user_id=user_id
    )

    member.delete()
    return redirect('team_detail', team_id=team.id)


@login_required
def profile(request):
    owned_teams = Team.objects.filter(owner=request.user)

    member_teams = Team.objects.filter(
        members=request.user
    ).exclude(owner=request.user)

    owned_tournaments = Tournament.objects.filter(owner=request.user)

    member_tournaments = Tournament.objects.filter(
        tournamentteam__team__members=request.user
    ).exclude(owner=request.user).distinct()

    context = {
        'owned_teams': owned_teams,
        'member_teams': member_teams,
        'owned_tournaments': owned_tournaments,
        'member_tournaments': member_tournaments,
    }

    return render(request, 'profile.html', context)


@login_required
def create_tournament(request):
    if request.method == 'POST':
        Tournament.objects.create(
            name=request.POST['name'],
            image=request.FILES.get('image'),
            owner=request.user
        )
        return redirect('lobby')

    return render(request, 'create_tournament.html')

@login_required
def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    is_owner = tournament.owner == request.user

    is_team_member = TournamentTeam.objects.filter(
        tournament=tournament,
        team__teammember__user=request.user
    ).exists()

    if not is_owner and not is_team_member:
        return HttpResponseForbidden()

    teams_in_tournament = TournamentTeam.objects.filter(
        tournament=tournament
    ).select_related('team')

    matches = Match.objects.filter(
        tournament=tournament
    ).select_related('home_team', 'away_team').order_by('round_number')

    # -------------------------
    # TABLA DE POSICIONES
    # -------------------------
    table = {}

    for tt in teams_in_tournament:
        team = tt.team
        table[team.id] = {
            'team': team,
            'PJ': 0,
            'PG': 0,
            'PE': 0,
            'PP': 0,
            'GF': 0,
            'GC': 0,
            'DG': 0,
            'PTS': 0,
        }

    played_matches = matches.filter(played=True)

    for match in played_matches:
        home = match.home_team
        away = match.away_team

        home_entry = table[home.id]
        away_entry = table[away.id]

        home_entry['PJ'] += 1
        away_entry['PJ'] += 1

        home_entry['GF'] += match.home_goals
        home_entry['GC'] += match.away_goals
        away_entry['GF'] += match.away_goals
        away_entry['GC'] += match.home_goals

        if match.home_goals > match.away_goals:
            home_entry['PG'] += 1
            home_entry['PTS'] += 3
            away_entry['PP'] += 1
        elif match.home_goals < match.away_goals:
            away_entry['PG'] += 1
            away_entry['PTS'] += 3
            home_entry['PP'] += 1
        else:
            home_entry['PE'] += 1
            away_entry['PE'] += 1
            home_entry['PTS'] += 1
            away_entry['PTS'] += 1

        # Diferencia de goles
        home_entry['DG'] = home_entry['GF'] - home_entry['GC']
        away_entry['DG'] = away_entry['GF'] - away_entry['GC']

    standings = sorted(
        table.values(),
        key=lambda x: (x['PTS'], x['DG'], x['GF']),
        reverse=True
    )

    return render(request, 'tournament_detail.html', {
        'tournament': tournament,
        'teams_in_tournament': teams_in_tournament,
        'matches': matches,
        'is_owner': is_owner,
        'standings': standings
    })



@login_required
def edit_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.owner != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        tournament.name = request.POST['name']

        if 'image' in request.FILES:
            tournament.image = request.FILES['image']

        tournament.save()
        return redirect('tournament_detail', tournament_id=tournament.id)

    return render(request, 'edit_tournament.html', {
        'tournament': tournament
    })

@login_required
def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.owner != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        tournament.delete()
        return redirect('lobby')

    return render(request, 'delete_tournament.html', {
        'tournament': tournament
    })

@login_required
def add_team_to_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Solo el creador del torneo puede inscribir equipos
    if tournament.owner != request.user:
        return HttpResponseForbidden()

    # TODOS los equipos del sistema
    teams = Team.objects.all()

    if request.method == 'POST':
        team_id = request.POST['team_id']
        team = get_object_or_404(Team, id=team_id)

        TournamentTeam.objects.get_or_create(
            tournament=tournament,
            team=team
        )

        return redirect('tournament_detail', tournament_id=tournament.id)

    return render(request, 'add_team_to_tournament.html', {
        'tournament': tournament,
        'teams': teams
    })

    



@login_required
def remove_team_from_tournament(request, tournament_id, team_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    team = get_object_or_404(Team, id=team_id)

    # Seguridad
    if request.user != tournament.owner:
        return HttpResponseForbidden()

    #  BLOQUEO SI YA HAY PARTIDOS
    has_matches = Match.objects.filter(tournament=tournament).exists()

    if has_matches:
        messages.error(
            request,
            "No puedes quitar equipos porque el torneo ya tiene partidos generados."
        )
        return redirect('tournament_detail', tournament_id=tournament.id)

    TournamentTeam.objects.filter(
        tournament=tournament,
        team=team
    ).delete()

    messages.success(request, "Equipo retirado del torneo.")
    return redirect('tournament_detail', tournament_id=tournament.id)


@login_required
def generate_matches(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Seguridad: solo el creador del torneo
    if request.user != tournament.owner:
        return redirect('tournament_detail', tournament_id=tournament.id)

    teams = list(
        Team.objects.filter(tournamentteam__tournament=tournament)
    )


    Match.objects.filter(tournament=tournament).delete()

    num_teams = len(teams)

    if num_teams % 2 != 0:
        teams.append(None)
        num_teams += 1

    rounds = num_teams - 1
    half = num_teams // 2

    for round_number in range(1, rounds + 1):
        for i in range(half):
            home = teams[i]
            away = teams[num_teams - 1 - i]

            if home is not None and away is not None:
                Match.objects.create(
                    tournament=tournament,
                    home_team=home,
                    away_team=away,
                    round_number=round_number
                )

        # Rotación de equipos (round-robin)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]

    return redirect('tournament_detail', tournament_id=tournament.id)

@login_required
def record_match_result(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Solo el creador del torneo puede registrar resultados
    if request.user != match.tournament.owner:
        return HttpResponseForbidden()

    if request.method == 'POST':
        match.home_goals = int(request.POST['home_goals'])
        match.away_goals = int(request.POST['away_goals'])
        match.played = True
        match.save()

        return redirect('tournament_detail', tournament_id=match.tournament.id)

    return render(request, 'record_match_result.html', {
        'match': match
    })
