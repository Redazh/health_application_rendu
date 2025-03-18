from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Profile
from .models import Group
from datetime import datetime
from datetime import date
from .models import QuestionnaireResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Friendship
from django.contrib.auth.models import User
from django.db.models import Q
import random
from django.shortcuts import get_object_or_404

################################ Gestion groupe ###########################
###########################################################################
# Récupérer les détails d'un groupe
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_group_details(request, group_id):
    """Récupère les détails d'un groupe spécifique"""
    group = get_object_or_404(Group, id=group_id)
    
    members = [{"username": user.username} for user in group.members.all()]
    is_admin = request.user == group.owner

    return Response({"id": group.id, "name": group.name, "members": members, "is_admin": is_admin})

# Renommer un groupe (seul l'admin peut le faire)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rename_group(request):
    """Renomme un groupe (seul l'admin peut modifier le nom)"""
    user = request.user
    group_id = request.data.get("group_id")
    new_name = request.data.get("new_name")

    if not new_name:
        return Response({"error": "Un nouveau nom est requis"}, status=400)

    group = get_object_or_404(Group, id=group_id)

    if group.owner != user:
        return Response({"error": "Seul l'administrateur peut renommer le groupe"}, status=403)

    group.name = new_name
    group.save()

    return Response({"message": "Groupe renommé avec succès", "new_name": group.name})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_groups(request):
    """Retourne uniquement les groupes auxquels l'utilisateur appartient"""
    user = request.user
    groups = Group.objects.filter(members=user).distinct() | Group.objects.filter(owner=user).distinct()

    group_list = [{"id": g.id, "name": g.name, "is_admin": (g.owner == user)} for g in groups]
    
    return Response(group_list)


# Créer un groupe
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    user = request.user
    name = request.data.get('name')

    if not name:
        return Response({'error': 'Nom du groupe requis'}, status=400)

    group = Group.objects.create(name=name, owner=user)
    group.members.add(user)  # Ajoute le créateur comme membre
    return Response({'message': 'Groupe créé', 'group': {'id': group.id, 'name': group.name}}, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member(request):
    user = request.user
    group_id = request.data.get('group_id')
    username = request.data.get('username')

    group = get_object_or_404(Group, id=group_id)
    new_member = get_object_or_404(User, username=username)

    if group.owner != user:
        return Response({'error': 'Seul l’administrateur peut ajouter des membres'}, status=403)

    if new_member in group.members.all():
        return Response({'error': 'Cet utilisateur est déjà dans le groupe'}, status=400)

    # Vérifier si `new_member` est un ami de `user`
    is_friend = Friendship.objects.filter(
        (Q(sender=user, receiver=new_member) | Q(sender=new_member, receiver=user)),
        status="accepted"
    ).exists()

    if not is_friend:
        return Response({'error': 'Vous ne pouvez ajouter que des amis dans ce groupe'}, status=400)

    group.members.add(new_member)
    return Response({'message': f'Utilisateur {username} ajouté au groupe'}, status=200)

# Supprimer un membre du groupe
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_member(request):
    user = request.user
    group_id = request.data.get('group_id')
    username = request.data.get('username')

    group = get_object_or_404(Group, id=group_id)
    member = get_object_or_404(User, username=username)

    if group.owner != user:
        return Response({'error': 'Seul l’administrateur peut supprimer des membres'}, status=403)

    if member == group.owner:
        return Response({'error': 'Le propriétaire ne peut pas se supprimer lui-même'}, status=400)

    group.members.remove(member)
    return Response({'message': f'Utilisateur {username} supprimé du groupe'}, status=200)

# Supprimer un groupe
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_group(request):
    user = request.user
    group_id = request.data.get('group_id')

    group = get_object_or_404(Group, id=group_id)

    if group.owner != user:
        return Response({'error': 'Seul l’administrateur peut supprimer ce groupe'}, status=403)

    group.delete()
    return Response({'message': 'Groupe supprimé'}, status=200)

# Quitter un groupe
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_group(request):
    user = request.user
    group_id = request.data.get('group_id')

    group = get_object_or_404(Group, id=group_id)

    if group.owner == user:
        return Response({'error': 'L’administrateur ne peut pas quitter son propre groupe'}, status=400)

    group.members.remove(user)
    return Response({'message': 'Vous avez quitté le groupe'}, status=200)

################################ Gestion amis #############################
###########################################################################

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ignore_suggestion(request):
    """Supprime temporairement un utilisateur des suggestions"""
    ignored_username = request.data.get('ignored_username')

    if not ignored_username:
        return Response({'error': 'Nom d’utilisateur requis'}, status=400)

    try:
        ignored_user = User.objects.get(username=ignored_username)

        # Ajouter l'utilisateur à une liste ignorée dans la session (peut être stocké en BDD si besoin)
        if 'ignored_users' not in request.session:
            request.session['ignored_users'] = []
        
        request.session['ignored_users'].append(ignored_user.id)
        request.session.modified = True  # Sauvegarder la session

        return Response({'message': f'Utilisateur {ignored_user.username} ignoré'})
    
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggest_friends(request):
    """Retourne 4-5 suggestions d'amis en excluant les amis existants"""
    user = request.user

    try:
        # Récupérer les amis actuels et les demandes en attente
        existing_friendships = Friendship.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )

        # Construire la liste des utilisateurs à exclure
        friend_ids = {user.id}
        for friendship in existing_friendships:
            friend_ids.add(friendship.sender.id)
            friend_ids.add(friendship.receiver.id)

        # Sélectionner les utilisateurs qui ne sont pas déjà amis
        potential_friends = User.objects.exclude(id__in=friend_ids)

        # Prendre jusqu'à 5 suggestions aléatoires
        suggestions = list(potential_friends)
        random.shuffle(suggestions)
        suggestions = suggestions[:5]

        return Response([{"username": u.username, "email": u.email} for u in suggestions])

    except Exception as e:
        return Response({"error": f"Erreur serveur: {str(e)}"}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    """Envoyer une demande d'ami si aucune relation n'existe déjà"""
    receiver_username = request.data.get('receiver')

    if not receiver_username:
        return Response({'error': 'Nom d’utilisateur requis'}, status=400)

    try:
        receiver = User.objects.get(username=receiver_username)

        if receiver == request.user:
            return Response({'error': 'Vous ne pouvez pas vous ajouter en ami'}, status=400)

        # Vérifier si une relation existe déjà
        existing_friendship = Friendship.objects.filter(
            Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
        ).exists()

        if existing_friendship:
            return Response({'error': 'Vous êtes déjà amis ou une demande est en attente'}, status=400)

        # Créer la demande d'ami
        Friendship.objects.create(sender=request.user, receiver=receiver, status="pending")
        return Response({'message': 'Demande d’amitié envoyée'}, status=201)

    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

    except Exception as e:
        return Response({'error': f"Erreur serveur: {str(e)}"}, status=500)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_friend_request(request):
    """Accepter ou refuser une demande d'ami"""
    sender_username = request.data.get('sender')
    action = request.data.get('action')  # "accept" ou "decline"

    if not sender_username or action not in ["accept", "decline"]:
        return Response({'error': 'Requête invalide'}, status=400)

    try:
        print(f"🔍 Requête reçue - sender: {sender_username}, action: {action}")  

        sender = User.objects.get(username=sender_username)

        friendship = Friendship.objects.get(sender=sender, receiver=request.user, status="pending")
        print(f"Demande d'ami trouvée: {friendship}")  

        if action == "accept":
            friendship.status = "accepted"
            friendship.save()
            print("Amitié acceptée !") 
            return Response({'message': f'Amitié acceptée avec {sender_username}'}, status=200)

        elif action == "decline":
            friendship.delete()
            print("Amitié refusée et supprimée")  
            return Response({'message': f'Demande refusée de {sender_username}'}, status=200)

    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

    except Friendship.DoesNotExist:
        return Response({'error': 'Aucune demande en attente trouvée'}, status=404)

    except Exception as e:
        return Response({'error': f'Erreur serveur: {str(e)}'}, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    """Lister les amis de l'utilisateur"""
    friends = Friendship.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status="accepted"
    )

    friend_list = []
    for friendship in friends:
        friend = friendship.sender if friendship.receiver == request.user else friendship.receiver
        friend_list.append({'username': friend.username, 'email': friend.email})

    return Response(friend_list)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_requests(request):
    """Lister les demandes d'ami en attente"""
    requests = Friendship.objects.filter(receiver=request.user, status="pending")
    pending_list = [{'username': req.sender.username, 'email': req.sender.email} for req in requests]

    return Response(pending_list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_friend(request):
    """Supprimer un ami"""
    friend_username = request.data.get('friend')

    try:
        friend = User.objects.get(username=friend_username)
        friendship = Friendship.objects.filter(
            (Q(sender=request.user, receiver=friend) | Q(sender=friend, receiver=request.user)),
            status="accepted"
        )
        
        if not friendship.exists():
            return Response({'error': 'Vous n’êtes pas amis avec cet utilisateur'}, status=400)

        friendship.delete()
        return Response({'message': f'Amitié supprimée avec {friend_username}'}, status=200)

    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=404)

################################## Login + inscription ##################################
#########################################################################################

from datetime import datetime
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Profile
from rest_framework.response import Response
from datetime import date
from .models import QuestionnaireResponse

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    date_naissance_str = request.data.get('date_naissance')
    poids = request.data.get('poids')
    taille = request.data.get('taille')
    objectif_de_pas_quotidien = request.data.get('objectif_de_pas_quotidien')
    genre = request.data.get('genre')
    profession = request.data.get('profession')
    user_goal = request.data.get('user_goal')
    activite_physique = request.data.get('activite_physique')
    composition_corporelle = request.data.get('composition_corporelle')
    indicateurs_cardio = request.data.get('indicateurs_cardio')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Ce nom d’utilisateur existe déjà'}, status=400)

    # Créer l'utilisateur
    user = User.objects.create_user(username=username, password=password)

    # Convertir la date de naissance
    date_naissance = datetime.strptime(date_naissance_str, "%Y-%m-%d").date() if date_naissance_str else None

    # Créer le profil avec les nouvelles informations
    Profile.objects.create(
        user=user,
        date_naissance=date_naissance,
        poids=poids,
        taille=taille,
        objectif_de_pas_quotidien=objectif_de_pas_quotidien,
        genre=genre,
        profession=profession,
        user_goal=user_goal,
        activite_physique=activite_physique,
        composition_corporelle=composition_corporelle,
        indicateurs_cardio=indicateurs_cardio
    )

    return Response({
        "message": "Inscription réussie",
        "user_id": user.id,
        "username": user.username
    }, status=200)



@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)

        try:
            profile = Profile.objects.get(user=user)
            fitbit_token = profile.fitbit_access_token
            fitbit_refresh_token = profile.fitbit_refresh_token
            fitbit_user_id = profile.fitbit_user_id
        except Profile.DoesNotExist:
            fitbit_token = None
            fitbit_refresh_token = None
            fitbit_user_id = None

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'fitbit_access_token': fitbit_token,
            'fitbit_refresh_token': fitbit_refresh_token,
            'fitbit_user_id': fitbit_user_id,
        })
    return Response({'error': 'Identifiants invalides'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access
def get_user_profile(request):
    user = request.user  # Get the logged-in user
    try:
        profile = Profile.objects.get(user=user)
        return Response({
            'username': user.username,
            'email': user.email,
            'date_naissance': profile.date_naissance,  
            'age': profile.age,
            'poids': profile.poids,
            'taille': profile.taille,
            'objectif_de_pas_quotidien': profile.objectif_de_pas_quotidien,
            'genre': profile.genre,
            'stress_level': profile.stress_level,
            'profession': profile.profession,  
            'user_goal': profile.user_goal,  
            'activite_physique' : profile.activite_physique,
            'composition_corporelle' : profile.composition_corporelle,
            'indicateurs_cardio' : profile.indicateurs_cardio
            })
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=404)

####################################  Connexion google ################################
#######################################################################################
  
from rest_framework.decorators import api_view
from rest_framework.response import Response
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.views import LoginView
from django.contrib.auth import get_user_model
import requests
from .models import Profile

User = get_user_model()

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

@api_view(['POST'])
def google_auth(request):
    code = request.data.get("code")
    if not code:
        return Response({"error": "Code OAuth manquant"}, status=400)

    # Exchange the code for an access token from Google
    data = {
        "code": code,
        "client_id": "278704582350-en3kaen8kes3m412klp3l1s341feeth7.apps.googleusercontent.com",
        "client_secret": "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",
        "redirect_uri": "http://localhost:8100",
        "grant_type": "authorization_code",
    }
    
    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    token_response = response.json()

    if "access_token" not in token_response:
        return Response({"error": "Échec de l'authentification Google"}, status=400)

    access_token = token_response["access_token"]

    # Get user info from Google
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info = user_info_response.json()

    email = user_info.get("email")
    name = user_info.get("name")

    if not email:
        return Response({"error": "Impossible de récupérer l'email depuis Google"}, status=400)

    # Check if user already exists
    user, created = User.objects.get_or_create(username=email, defaults={"email": email})
    user_id = User.objects.filter(email=email).values_list("id", flat=True).first()
    
    try:
        profile = Profile.objects.get(user=user)
        fitbit_token = profile.fitbit_access_token
        fitbit_refresh_token = profile.fitbit_refresh_token
        fitbit_user_id = profile.fitbit_user_id
    except Profile.DoesNotExist:
        fitbit_token = None
        fitbit_refresh_token = None
        fitbit_user_id = None
        
    print("🔑 User ID:", user_id)  
    # Check if profile exists
    if created:
        is_new_user = True  # User already has a profile
    else:
        is_new_user = False  # User is new and needs to complete the profile

    # Generate a JWT Token
    refresh = RefreshToken.for_user(user)

    return Response({
        "user_id": user_id,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "email": email,
        "name": name,
        "is_new_user": is_new_user,
        "fitbit_access_token": fitbit_token,
        "fitbit_refresh_token": fitbit_refresh_token,
        "fitbit_user_id": fitbit_user_id,
    })
    
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_profile(request):
    user = request.user
    print("USEEEEER",user)
    try:
        profile, created = Profile.objects.get_or_create(user=user)
        user_id = User.objects.filter(email=user).values_list("id", flat=True).first()

        date_naissance_str = request.data.get("date_naissance")
        if date_naissance_str:
            profile.date_naissance = datetime.strptime(date_naissance_str, "%Y-%m-%d").date()
        
        profile.poids = request.data.get("poids")
        profile.taille = request.data.get("taille")
        profile.objectif_de_pas_quotidien = request.data.get("objectif_de_pas_quotidien")
        profile.genre = request.data.get("genre")
        profile.profession = request.data.get("profession")
        profile.user_goal = request.data.get("user_goal")
        profile.activite_physique = request.data.get("activite_physique")
        profile.composition_corporelle = request.data.get("composition_corporelle")
        profile.indicateurs_cardio = request.data.get("indicateurs_cardio")
        profile.save()

        return Response({"success": "Profil mis à jour avec succès"}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

############################################### Questionnaire #####################################
###################################################################################################

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questionnaire(request):
    user = request.user
    today = date.today()

    # Vérifie si l'utilisateur a déjà répondu aujourd’hui
    if QuestionnaireResponse.objects.filter(user=user, date=today).exists():
        return Response({"message": "Questionnaire déjà rempli aujourd'hui."})

    # Retourne la liste des questions si l'utilisateur n'a pas encore répondu
    return Response({"questions": QUESTIONS})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_questionnaire(request):
    user = request.user
    today = date.today()

    # Vérifie si l'utilisateur a déjà répondu aujourd’hui
    if QuestionnaireResponse.objects.filter(user=user, date=today).exists():
        return Response({"message": "Vous avez déjà répondu aujourd’hui."}, status=400)

    responses = request.data.get("responses")

    if not responses:
        return Response({"error": "Aucune réponse fournie."}, status=400)

    # Mapping des réponses textuelles en valeurs numériques
    response_mapping = {
        "Never": 0,
        "Almost Never": 1,
        "Sometimes": 2,
        "Fairly Often": 3,
        "Very Often": 4
    }

    # Convertir les réponses en valeurs numériques
    scores = {key: response_mapping[value] for key, value in responses.items()}

    # Inverser les scores des questions 2,3
    for key in ["q2", "q3"]:
        if key in scores:
            scores[key] = 4 - scores[key]

    # Calculer le score total de stress
    stress_score = sum(scores.values())

    # Déterminer la catégorie de stress
    stress_level = "Faible stress" if stress_score <= 5 else "Stress modéré" if stress_score <= 10 else "Stress élevé"

    # Mettre à jour le profil de l'utilisateur
    profile, created = Profile.objects.get_or_create(user=user)
    profile.stress_level = stress_score  # Met à jour le niveau de stress
    profile.save()

    # Enregistrer les réponses et le score dans QuestionnaireResponse
    QuestionnaireResponse.objects.create(
        user=user,
        responses=responses,
        stress_score=stress_score,
        date=today
    )

    return Response({
        "message": "Réponses enregistrées avec succès !",
        "stress_score": stress_score,
        "stress_level": stress_level
    })

QUESTIONS = [
    {
        "question": "In the last week, how often have you felt that you were unable to control the important things in your life?",
        "options": ["Never", "Almost Never", "Sometimes", "Fairly Often", "Very Often"]
    },
    {
        "question": "In the last week, how often have you felt confident about your ability to handle your personal problems?",
        "options": ["Never", "Almost Never", "Sometimes", "Fairly Often", "Very Often"]
    },
    {
        "question": "In the last week, how often have you felt that things were going your way?",
        "options": ["Never", "Almost Never", "Sometimes", "Fairly Often", "Very Often"]
    },
    {
        "question": "In the last week, how often have you felt difficulties were piling up so high that you could not overcome them?",
        "options": ["Never", "Almost Never", "Sometimes", "Fairly Often", "Very Often"]
    }
]


###############################################################################################
###############################################################################################





import requests
import json
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import json
import base64

@csrf_exempt
def fitbit_auth(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code")
            user_id = data.get("user_id")
            user = User.objects.get(id=user_id)
            if not code:
                return JsonResponse({"error": "Authorization code is missing"}, status=400)

            CLIENT_ID = "23Q39R"  # Replace with your actual Fitbit Client ID
            CLIENT_SECRET = "827dc7361f76cbc28d06236e40374945"  # Replace with your actual Client Secret
            REDIRECT_URI = "http://localhost:8100/callback2"

            # Encode client credentials
            credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Fitbit Token Exchange API
            token_url = "https://api.fitbit.com/oauth2/token"
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            body = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code": code,
            }

            # Request the token from Fitbit API
            response = requests.post(token_url, data=body, headers=headers)
            fitbit_data = response.json()
            
            if "access_token" in fitbit_data:
                profile, created = Profile.objects.get_or_create(user=user)
                profile.fitbit_user_id = fitbit_data["user_id"]
                profile.fitbit_access_token = fitbit_data["access_token"]
                profile.fitbit_refresh_token = fitbit_data["refresh_token"]
                profile.fitbit_token_expires = now() + timedelta(seconds=fitbit_data["expires_in"])
                profile.save()
                return JsonResponse(fitbit_data, status=200)  # Return access token
            else:
                return JsonResponse(fitbit_data, status=response.status_code)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_fitbit_token(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
        refresh_token = profile.fitbit_refresh_token

        if not refresh_token:
            return Response({"error": "No Fitbit refresh token found"}, status=400)
        
        CLIENT_ID = "23Q39R"
        CLIENT_SECRET = "827dc7361f76cbc28d06236e40374945"

        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

            # Fitbit Token Exchange API
        token_url = "https://api.fitbit.com/oauth2/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        body = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        response = requests.post(token_url, data=body, headers=headers)
        data = response.json()

        if "access_token" in data:
            # Save new tokens in the database
            profile.fitbit_access_token = data["access_token"]
            profile.fitbit_refresh_token = data["refresh_token"] 
            profile.save()

            return Response({
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"]
            })
        else:
            return Response(data, status=400)

    except Profile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=404)
    
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
from .models import FitbitData, Profile
from .utils import refresh_fitbit_token
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_and_store_fitbit_activity(request):
    user = request.user  # Récupérer l'utilisateur authentifié
    profile = Profile.objects.filter(user=user).first()

    if not profile or not profile.fitbit_access_token:
        return Response({"error": "Aucun compte Fitbit lié."}, status=400)

    token = profile.fitbit_access_token  # Récupérer le token Fitbit depuis la DB
    headers = {"Authorization": f"Bearer {token}"}

    # Liste des activités à récupérer
    endpoints = {
        "steps": "activities/steps",
        "minutesSedentary": "activities/minutesSedentary",
        "minutesLightlyActive": "activities/minutesLightlyActive",
        "minutesFairlyActive": "activities/minutesFairlyActive",
        "minutesVeryActive": "activities/minutesVeryActive",
        "distance": "activities/distance",
        "calories": "activities/calories"
    }

    fitbit_data = {}

    for key, endpoint in endpoints.items():
        url = f"https://api.fitbit.com/1/user/-/{endpoint}/date/today/1d.json"
        response = requests.get(url, headers=headers)

        # Si le token est expiré, on tente de le rafraîchir
        if response.status_code == 401:
            print(f"⚠ Token expiré pour {key}, tentative de rafraîchissement...")
            token = refresh_fitbit_token(user)
            if not token:
                return Response({"error": "Impossible de rafraîchir le token Fitbit."}, status=401)
            
            headers["Authorization"] = f"Bearer {token}"
            response = requests.get(url, headers=headers)  # Relancer la requête
        
        if response.status_code == 200:
            data = response.json()
            activity_key = f"activities-{key}"
            if activity_key in data and len(data[activity_key]) > 0:
                value = data[activity_key][0].get("value", 0)
                fitbit_data[key] = float(value)
            else:
                print(f"Données Fitbit manquantes pour {key}, valeur mise à 0")
                fitbit_data[key] = 0
        else:
            print(f"Erreur lors de la récupération de {key}")
            print(response.json())
            fitbit_data[key] = 0

    # Récupérer la durée de sommeil séparément
    sleep_url = "https://api.fitbit.com/1.2/user/-/sleep/date/today.json"
    response = requests.get(sleep_url, headers=headers)
    if response.status_code == 200:
        sleep_data = response.json()
        if sleep_data.get("sleep"):
            fitbit_data["sleep_duration"] = round(
                sleep_data["sleep"][0]["duration"] / (1000 * 60 * 60), 2
            )  # Convertir les ms en heures
        else:
            fitbit_data["sleep_duration"] = 0
    else:
        fitbit_data["sleep_duration"] = 0

    fitbit_record, created = FitbitData.objects.get_or_create(user=user, date=timezone.now().date())

    if created:
        print(f"NOUVEAU FitbitData créé pour {user.username}")
    else:
        print(f"FitbitData déjà existant pour {user.username}")

    # Mise à jour des données
    fitbit_record.date = timezone.now().date()
    fitbit_record.steps = fitbit_data["steps"]
    fitbit_record.sedentary_minutes = fitbit_data["minutesSedentary"]
    fitbit_record.lightly_active_minutes = fitbit_data["minutesLightlyActive"]
    fitbit_record.fairly_active_minutes = fitbit_data["minutesFairlyActive"]
    fitbit_record.very_active_minutes = fitbit_data["minutesVeryActive"]
    fitbit_record.distance = fitbit_data["distance"]
    fitbit_record.calories = fitbit_data["calories"]
    fitbit_record.sleep_duration = fitbit_data["sleep_duration"]
    fitbit_record.save()

    return Response({"message": "Données Fitbit mises à jour.", "data": fitbit_data})

from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from .models import FitbitData, Profile, FitbitDataHistory

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_and_store_yesterdays_fitbit_activity(request):
    user = request.user  # Récupérer l'utilisateur authentifié
    profile = Profile.objects.filter(user=user).first()

    if not profile or not profile.fitbit_access_token:
        return Response({"error": "Aucun compte Fitbit lié."}, status=400)

    token = profile.fitbit_access_token  # Récupérer le token Fitbit depuis la DB
    headers = {"Authorization": f"Bearer {token}"}

    # Déterminer la date d'hier au format "YYYY-MM-DD"
    yesterday = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Liste des activités à récupérer
    endpoints = {
        "steps": "activities/steps",
        "minutesSedentary": "activities/minutesSedentary",
        "minutesLightlyActive": "activities/minutesLightlyActive",
        "minutesFairlyActive": "activities/minutesFairlyActive",
        "minutesVeryActive": "activities/minutesVeryActive",
        "distance": "activities/distance",
        "calories": "activities/calories"
    }

    fitbit_data = {}

    for key, endpoint in endpoints.items():
        url = f"https://api.fitbit.com/1/user/-/{endpoint}/date/{yesterday}/1d.json"
        response = requests.get(url, headers=headers)

        # Si le token est expiré, on tente de le rafraîchir
        if response.status_code == 401:
            print(f"⚠ Token expiré pour {key}, tentative de rafraîchissement...")
            token = refresh_fitbit_token(user)
            if not token:
                return Response({"error": "Impossible de rafraîchir le token Fitbit."}, status=401)
            
            headers["Authorization"] = f"Bearer {token}"
            response = requests.get(url, headers=headers)  # Relancer la requête
        
        if response.status_code == 200:
            data = response.json()
            activity_key = f"activities-{key}"
            if activity_key in data and len(data[activity_key]) > 0:
                value = data[activity_key][0].get("value", 0)
                fitbit_data[key] = float(value)
            else:
                print(f"Données Fitbit manquantes pour {key}, valeur mise à 0")
                fitbit_data[key] = 0
        else:
            print(f"Erreur lors de la récupération de {key}")
            print(response.json())
            fitbit_data[key] = 0

    # Récupérer la durée de sommeil pour hier séparément
    sleep_url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{yesterday}.json"
    response = requests.get(sleep_url, headers=headers)
    if response.status_code == 200:
        sleep_data = response.json()
        if sleep_data.get("sleep"):
            fitbit_data["sleep_duration"] = round(
                sleep_data["sleep"][0]["duration"] / (1000 * 60 * 60), 2
            )  # Convertir les ms en heures
        else:
            fitbit_data["sleep_duration"] = 0
    else:
        fitbit_data["sleep_duration"] = 0

    # Récupérer ou créer une entrée pour la date d'hier
    fitbit_record = FitbitDataHistory.objects.filter(user=user, date=yesterday).first()

    if fitbit_record is None:
        fitbit_record = FitbitDataHistory(user=user, date=yesterday)
        print(f"NOUVEAU FitbitData créé pour {user.username} (Date: {yesterday})")
    else:
        print(f"FitbitData mis à jour pour {user.username} (Date: {yesterday})")

    # Mise à jour des données
    fitbit_record.date = yesterday
    fitbit_record.steps = fitbit_data["steps"]
    fitbit_record.sedentary_minutes = fitbit_data["minutesSedentary"]
    fitbit_record.lightly_active_minutes = fitbit_data["minutesLightlyActive"]
    fitbit_record.fairly_active_minutes = fitbit_data["minutesFairlyActive"]
    fitbit_record.very_active_minutes = fitbit_data["minutesVeryActive"]
    fitbit_record.distance = fitbit_data["distance"]
    fitbit_record.calories = fitbit_data["calories"]
    fitbit_record.sleep_duration = fitbit_data["sleep_duration"]
    fitbit_record.save()

    return Response({"message": "Données Fitbit de la veille mises à jour.", "data": fitbit_data})


###########################################################################
###########################################################################

from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FitbitDataHistory

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fitbit_history(request):
    user = request.user
    selected_date = request.GET.get("date")  # Get selected date from the frontend

    if not selected_date:
        return Response({"error": "No date provided."}, status=400)

    try:
        fitbit_data = FitbitDataHistory.objects.get(user=user, date=selected_date)
        return Response({
            "date": fitbit_data.date,
            "steps": fitbit_data.steps,
            "sedentary_minutes": fitbit_data.sedentary_minutes,
            "lightly_active_minutes": fitbit_data.lightly_active_minutes,
            "fairly_active_minutes": fitbit_data.fairly_active_minutes,
            "very_active_minutes": fitbit_data.very_active_minutes,
            "distance": fitbit_data.distance,
            "calories": fitbit_data.calories,
            "sleep_duration": fitbit_data.sleep_duration,
        })
    except FitbitDataHistory.DoesNotExist:
        return Response({"error": f"No stored data for {selected_date}."}, status=404)



##########################################################################################
############ recommandation ############################

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .recommandation import get_workout_recommendation, get_recipe_recommendation,record_workout_completion,calcul_besoins_energetiques ,infer_values_from_cluster_v2
from .models import WorkoutProgram, UserWeeklyRecommendation, WorkoutProgramClusterRating
import hashlib


from django.utils.timezone import now, timedelta
from django.db.models import Avg


def generate_workout_hash(workout_json):
    """
    Génère un hash unique basé sur les exercices sans tenir compte des jours.
    """
    exercises_list = []
    for details in workout_json.values():  # Ignore les jours
        for exo in details.get("exercises", []):
            exercises_list.append((exo["name"], exo["duration"], exo["repetitions"], eval(exo["caloriesBurned"].split('=')[0])))

    # Trier pour que l'ordre n'ait pas d'importance
    exercises_list.sort()
    hash_string = json.dumps(exercises_list, sort_keys=True)
    
    return hashlib.sha1(hash_string.encode()).hexdigest()

def get_last_monday():
    """
    Retourne la date du dernier lundi.
    """
    today = now().date()
    days_since_monday = today.weekday()  # 0 = Lundi, ..., 6 = Dimanche
    return today - timedelta(days=days_since_monday)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_recommendation(request):
    """
        Génère une nouvelle recommandation chaque semaine.
        Vérifie si l'utilisateur a suivi la recommandation précédente avant de lui donner une nouvelle.
    """
    if request.method == "POST":
        try:
            user = request.user
            profile = user.profile 
            gender = "Male" if profile.genre.lower() == "homme" else "Female"
            age = int(profile.age) if int(profile.age) != 0 else 1
            user_data = {
                "user_id": profile.user_id,
                "age": age,
                "gender": gender,
                "height": int(profile.taille),
                "weight": int(profile.poids),
                "fitness_level": "moderate", ## will be updated in infer_values_from_cluster_v2
                "target_calories": 500,  ## will be updated in infer_values_from_cluster_v2
                "Workout Duration (mins)": 60, ## will be updated in infer_values_from_cluster_v2
                "user_goal": profile.user_goal,
                "profession": profile.profession,
                "stress_level": profile.stress_level,
                "cluster_id": profile.assigned_cluster,
            }
            
            user_updated = infer_values_from_cluster_v2(user_data)
            user_data= user_updated
            baseline_calories = calcul_besoins_energetiques(user_data["age"], user_data["gender"], user_data["height"], user_data["weight"],  user_data["fitness_level"])
            user_data["target_calories"] = user_data["target_calories"] - baseline_calories["DEJ (kcal/jour)"] if user_data["target_calories"] > (baseline_calories["DEJ (kcal/jour)"]+200) else 500 
            print(user_data)
            cluster_id = user_data["cluster_id"] 

            last_monday = get_last_monday()

            # Vérifier s'il a une recommandation de la semaine dernière
            previous_recommendation = UserWeeklyRecommendation.objects.filter(
                user=user, week_start=last_monday - timedelta(days=7)
            ).first()

            requires_feedback = False
            previous_recommendation_id = None
            workout_program_id = None



            if previous_recommendation:
                requires_feedback = True
                previous_recommendation_id = previous_recommendation.id  # Envoyer l'ID au frontend
                workout_program_id = previous_recommendation.workout_program.id


                # Vérifier si le rating doit être demandé
                
                adherence_score = calculate_weekly_adherence(user, previous_recommendation,baseline_calories = baseline_calories["MB (kcal/jour)"])
                rating_value =  3 
                if adherence_score >= 6: #(6/7)
                    register_rating(user, previous_recommendation.workout_program, cluster_id, rating_value = rating_value)  

            # Générer une nouvelle recommandation

            # Vérifier s'il existe un programme bien noté dans le cluster
            high_rated_program = WorkoutProgramClusterRating.objects.filter(
                cluster_id=cluster_id, avg_rating__gt=2
            ).order_by("-avg_rating").first()

            if high_rated_program:
                print(f" Utilisation d'un programme bien noté du cluster {cluster_id}")
                workout_program = high_rated_program.workout_program
                workout_plan_json = workout_program.userweeklyrecommendation_set.first().recommendation_json
            else:
                # Générer une nouvelle recommandation
                print("Génération d'une nouvelle recommandation...")
                workout_plan_json, _ = get_workout_recommendation(user_data)


            meal_plan_json, _ = get_recipe_recommendation(user_data, workout_plan_json)
            
        
            workout_hash = generate_workout_hash(workout_plan_json)

            workout_program, created = WorkoutProgram.objects.get_or_create(hash=workout_hash)



            weekly_recommendation, created = UserWeeklyRecommendation.objects.get_or_create(
            user=user,
            week_start=last_monday,
            defaults={
                "workout_program": workout_program,
                "recommendation_json": workout_plan_json
            }
            )

            if not created:
                # Mettre à jour les champs si la recommandation existe déjà
                weekly_recommendation.workout_program = workout_program
                weekly_recommendation.recommendation_json = workout_plan_json
                weekly_recommendation.save()
                print(f"DEBUG: Recommandation mise à jour pour {user} - Semaine {last_monday}.")




            print(meal_plan_json)
            return JsonResponse({
                    "success": True,
                    "workout_plan": workout_plan_json,
                    "meal_plan": meal_plan_json,
                    "requires_feedback": requires_feedback,
                    "previous_recommendation_id": previous_recommendation_id,
                    "workout_program_id": workout_program_id,
                    "cluster_id": cluster_id
                }, safe=False)
        
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)




import datetime

def calculate_weekly_adherence(user, weekly_recommendation, baseline_calories=1500):
    """
    Vérifie l'adhérence d'un utilisateur à son programme d'entraînement sur 7 jours.
    """
    adherence_score = 0
    user_data_last_week = get_user_activity_data(user, weekly_recommendation.week_start + timedelta(days=7))

    # Transformer les dates en noms de jours pour la correspondance
    day_mapping = {}
    for date_str, data in user_data_last_week.items():
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime("%A")  # Convertir la date en "Monday", "Tuesday", etc.
        day_mapping[day_name] = data

    # Vérification de l'adhérence jour par jour
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        day_data = day_mapping.get(day, None)  # Récupère les données d'activité du jour
        day_recommendation = weekly_recommendation.recommendation_json.get(day, None)  # Récupère la recommandation

        if day_data and day_recommendation:
            adherence_score += record_workout_completion(day_data, day_recommendation, baseline_calories=baseline_calories)
        else:
            adherence_score += 0  # Si aucune donnée, considérer l'adhérence comme 0

    return adherence_score



def register_rating(user, workout_program, cluster_id, rating_value):
    """
    Enregistre un rating pour un programme si l'utilisateur a suivi 6 jours sur 7.
    """
    cluster_rating, created = WorkoutProgramClusterRating.objects.get_or_create(
        workout_program=workout_program, cluster_id=cluster_id
    )

    cluster_rating.avg_rating = ((cluster_rating.avg_rating * cluster_rating.rating_count) + rating_value) / (cluster_rating.rating_count + 1)
    cluster_rating.rating_count += 1
    cluster_rating.save()

def update_rating(workout_program, cluster_id, rating_value):
    print(f"DEBUG: update_rating() appelé pour workout_program={workout_program.id}, cluster_id={cluster_id}, rating_value={rating_value}")

    cluster_rating, created = WorkoutProgramClusterRating.objects.get_or_create(
        workout_program=workout_program, cluster_id=cluster_id
    )

    print(f"DEBUG: Avant mise à jour → avg_rating={cluster_rating.avg_rating}, rating_count={cluster_rating.rating_count}")

    if cluster_rating.rating_count > 1:
        cluster_rating.avg_rating = ((cluster_rating.avg_rating * cluster_rating.rating_count) - 3.5 + rating_value) / (cluster_rating.rating_count)
    else:
        cluster_rating.avg_rating = rating_value

    cluster_rating.save()
    print(f"DEBUG: Après mise à jour → avg_rating={cluster_rating.avg_rating}, rating_count={cluster_rating.rating_count}")




from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import FitbitDataHistory

def get_user_activity_data(user, start_date_str):
    """
    Fetch the last 7 days of Fitbit data from FitbitDataHistory starting from a given date.

    :param user: The user object.
    :param start_date_str: The starting date as a string (format: YYYY-MM-DD).
    :return: Dictionary with the last 7 days' data.
    """
    try:
        # Convert the string date to a datetime object
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        start_date = make_aware(start_date)  # Ensure timezone compatibility

        # Get the last 7 days of Fitbit data from start_date (including today)
        last_7_days = start_date - timedelta(days=6)  # 7-day range

        # Query FitbitDataHistory for the user in the given date range
        fitbit_records = FitbitDataHistory.objects.filter(
            user=user, date__range=[last_7_days, start_date]
        ).order_by("date")

        # Convert data to dictionary format
        user_data = {}
        for record in fitbit_records:
            user_data[record.date.strftime("%Y-%m-%d")] = {
                "calories": record.calories,
                "minutes_active": (
                    record.lightly_active_minutes +
                    record.fairly_active_minutes +
                    record.very_active_minutes
                ),
                "steps": record.steps,
                "distance": record.distance
            }

        return user_data

    except Exception as e:
        print(f"Error fetching Fitbit history: {str(e)}")
        return {}
    


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_feedback_rating(request):
    """
    Met à jour la note de la recommandation après que l'utilisateur ait donné un feedback.
    """
    try:
        recommendation_id = request.data.get("recommendation_id")
        rating_value = float(request.data.get("rating"))
        workout_program_id = request.data.get("workout_program_id")
        cluster_id = request.data.get("cluster_id")

        if not recommendation_id or not rating_value or not workout_program_id or not cluster_id:
            return JsonResponse({"success": False, "error": "Données manquantes"}, status=400)

        workout_program = WorkoutProgram.objects.get(id=workout_program_id)

        # Met à jour le rating en supprimant 3.5 et ajoutant la vraie note
        update_rating(workout_program, cluster_id, rating_value)

        return JsonResponse({"success": True, "message": "Rating mis à jour après feedback."})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)



############################################################################################
############################################################################################
import json
from datetime import timedelta
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Import pre-loaded models and classification functions
from .ml_models import df_aggregated, scaler, pca, centroids_df
from .classification import classify_new_users

from sklearn.decomposition import PCA
from .models import Profile, FitbitDataHistory  # adjust as needed
from sklearn.preprocessing import MinMaxScaler

# Compute cluster means (for numeric columns only)
df_means = df_aggregated.select_dtypes(include=['number']).groupby("Cluster").mean()
print("DEBUG: Cluster means computed:")
print(df_means)

# The features used for classification/PCA (excluding 'id' and 'Cluster')
features = df_aggregated.drop(columns=['id', 'Cluster'], errors='ignore')
print("DEBUG: Features used for PCA:")
print(features.columns.tolist())

def assign_cluster(activity_answer, body_metrics_answer, cardio_answer, gender):
    """
    Assigns a cluster based on questionnaire answers.
    """
    print("DEBUG: assign_cluster called with:",
          activity_answer, body_metrics_answer, cardio_answer, gender)
    answer_mapping = {"A": 1, "B": 2, "C": 3}
    pc1_score = answer_mapping.get(activity_answer.upper(), 0)
    pc2_score = answer_mapping.get(body_metrics_answer.upper(), 0)
    pc3_score = answer_mapping.get(cardio_answer.upper(), 0)
    
    # Special condition: if PC1 is high and either of the others is not
    if pc1_score == 3 and (pc2_score != 3 or pc3_score != 3):
        cluster = 4 if gender.upper() == "M" else 2
        print("DEBUG: Special condition met, returning cluster", cluster)
        return cluster

    # Mapping responses to clusters (adjust as needed)
    cluster_mapping = {
        (3, 3, 3): 1,
        (2, 3, 2): 4,
        (3, 2, 3): 3,
        (1, 2, 1): 5,
        (1, 1, 2): 5,
        (2, 1, 2): 2,
        (3, 1, 1): 5,
        (1, 1, 1): 5,
        (2, 2, 2): 3,
        (1, 3, 3): 4,
        (2, 3, 3): 3,
        (1, 2, 2): 5,
        (2, 2, 3): 3,
        (2, 1, 3): 2,
    }
    cluster = cluster_mapping.get((pc1_score, pc2_score, pc3_score), 5)
    print("DEBUG: assign_cluster mapping result:",
          (pc1_score, pc2_score, pc3_score), "->", cluster)
    return cluster

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def classify_new_user_view(request):
    """
    Classifies a user either using aggregated Fitbit data from the past week (if full 7 days are available)
    or, if not, using questionnaire responses stored on the user's profile.
    The classification is updated only once per week.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)

    try:
        print("DEBUG: classify_new_user_view called.")
        user = request.user  
        profile = Profile.objects.get(user=user)
        print("DEBUG: Retrieved profile for user:", user.username)
        
        one_week_ago = now() - timedelta(days=7)
        print("DEBUG: one_week_ago =", one_week_ago)
        
        # Check if classification was updated within the last week.
        if profile.last_cluster_update and profile.last_cluster_update >= one_week_ago:
            print("DEBUG: Returning stored classification from last week. Last update:",
                  profile.last_cluster_update)
            return JsonResponse({
                'assigned_cluster': profile.assigned_cluster,
                'pca_values': profile.pca_values
            })

        # Attempt to retrieve Fitbit data for the past week.
        fitbit_records = FitbitDataHistory.objects.filter(user=user, date__gte=one_week_ago)
        print("DEBUG: Retrieved", fitbit_records.count(), "Fitbit records for the past week.")
        use_fitbit = False

        if fitbit_records.exists():
            fitbit_df = pd.DataFrame.from_records(fitbit_records.values())
            print("DEBUG: Fitbit DataFrame head:")
            print(fitbit_df.head())
            # Check if there are data for 7 distinct days.
            distinct_days = fitbit_df['date'].nunique()
            print("DEBUG: Distinct days in Fitbit data:", distinct_days)
            if distinct_days >= 7:
                use_fitbit = True

        if use_fitbit:
            print("DEBUG: Using aggregated Fitbit data (full week available).")
            aggregated_data = {
                "calories": fitbit_df["calories"].mean(),
                "distance": fitbit_df["distance"].mean(),
                "steps": fitbit_df["steps"].mean(),
                "lightly_active_minutes": fitbit_df["lightly_active_minutes"].mean(),
                "sedentary_minutes": fitbit_df["sedentary_minutes"].mean(),
                # Use profile values; adjust if needed.
                "age": profile.age if profile.age is not None else 0,
                "gender": 1 if profile.genre == "femme" else 0,
                "bmi": (profile.poids / (profile.taille ** 2)) if profile.poids and profile.taille else 0,
                "resting_hr": 55,
                "bpm": 65
            }
            print("DEBUG: Aggregated Fitbit data:")
            print(aggregated_data)
            new_user_df = pd.DataFrame([aggregated_data])
            print("DEBUG: new_user_df from Fitbit data:")
            print(new_user_df)
            print("centroids before adding new user\n")
            print(centroids_df)
            # Classify using your existing classification function.
            assigned_clusters, _ = classify_new_users(new_user_df, scaler, pca, centroids_df, df_aggregated)
            assigned_cluster = int(assigned_clusters[0])
            print("DEBUG: Assigned cluster (Fitbit data):", assigned_cluster)
            
            # Fill missing features using cluster means from df_means.
            new_user_data_pca = aggregated_data.copy()
            cluster_means = df_means.loc[assigned_cluster]
            print("DEBUG: Cluster means for assigned cluster:")
            print(cluster_means)
            for col in features.columns:
                if col not in new_user_data_pca or pd.isnull(new_user_data_pca[col]):
                    new_user_data_pca[col] = cluster_means[col]
            print("DEBUG: new_user_data_pca after filling missing features:")
            print(new_user_data_pca)
            new_user_df_pca = pd.DataFrame([new_user_data_pca])[features.columns]
            print("DEBUG: new_user_df_pca:")
            print(new_user_df_pca)

            # --- Include the new user row in the training data ---
            df_aggregated_copy = df_aggregated.copy()
            new_user_row = new_user_df_pca.copy()
            new_user_row['Cluster'] = assigned_cluster
            df_combined = pd.concat([df_aggregated_copy, new_user_row], ignore_index=True)
            print("DEBUG: Combined data shape:", df_combined.shape)

            # Recompute PCA on the combined dataset.
            combined_features = df_combined.drop(columns=['id', 'Cluster'], errors='ignore')
            combined_scaled = scaler.transform(combined_features)
            combined_pca_result = pca.transform(combined_scaled)
            df_combined_pca = pd.DataFrame(combined_pca_result, columns=['PC1', 'PC2', 'PC3'])
            df_combined_pca['Cluster'] = df_combined['Cluster']
            # Invert PC1 so that more negative (better) becomes larger.
            # df_combined_pca['PC1'] = -df_combined_pca['PC1']
            # Print recomputed centroids after including the new user
            new_centroids = df_combined_pca.groupby('Cluster')[['PC1', 'PC2', 'PC3']].mean()
            print("DEBUG: Recomputed centroids after adding new user:")
            print(new_centroids)

            # Scale PCA scores to the 0–100 range.
            combined_minmax_scaler = MinMaxScaler(feature_range=(0, 100))
            df_combined_pca_scaled = pd.DataFrame(
                combined_minmax_scaler.fit_transform(df_combined_pca[['PC1', 'PC2', 'PC3']]),
                columns=['PC1_Score', 'PC2_Score', 'PC3_Score']
            )
            df_combined_pca_scaled['Cluster'] = df_combined_pca['Cluster']
            # Ensure sign consistency: Flip scores if PC1 of cluster 1 was flipped
            if centroids_df.loc[centroids_df['Cluster'] == 1, 'PC1'].values[0] > 0:
                print("DEBUG: Flipping PCA scores to maintain 0-100 coherence.")
                df_combined_pca_scaled[['PC1_Score', 'PC2_Score', 'PC3_Score']] = 100 - df_combined_pca_scaled[['PC1_Score', 'PC2_Score', 'PC3_Score']]
            # Invert the scaled PC1 score.
            df_combined_pca_scaled['PC1_Score'] = df_combined_pca_scaled['PC1_Score']
            print("DEBUG: Scaled PCA results head:")
            print(df_combined_pca_scaled.head())
            new_user_pca_scores = df_combined_pca_scaled.iloc[-1][['PC1_Score', 'PC2_Score', 'PC3_Score']]
            pca_values = new_user_pca_scores.tolist()
            print("DEBUG: Final PCA scores for new user:", pca_values)
        else:
            # Not enough Fitbit data available; use questionnaire answers stored in the profile.
            print("DEBUG: Insufficient Fitbit data; using questionnaire answers from the profile.")
            # Retrieve the metadata from the profile
            activity = profile.activite_physique
            body_metrics = profile.composition_corporelle
            cardio = profile.indicateurs_cardio
            gender_str = profile.genre  # assuming this field holds "M" or "F"
            print("DEBUG: Retrieved questionnaire values from profile:",
                  activity, body_metrics, cardio, gender_str)
            assigned_cluster = assign_cluster(activity, body_metrics, cardio, gender_str)
            print("DEBUG: Assigned cluster (questionnaire):", assigned_cluster)
            print("DEBUG: Using precomputed PCA centroids from ml_models.py")
            print(centroids_df)  # Debugging: Print centroids to confirm correctness

            if assigned_cluster in centroids_df['Cluster'].values:
                raw_pca_values = centroids_df.loc[centroids_df['Cluster'] == assigned_cluster, ['PC1', 'PC2', 'PC3']].values.flatten()
            else:
                raw_pca_values = [None, None, None]

            print("DEBUG: Raw PCA values before scaling:", raw_pca_values)

            if None not in raw_pca_values:  # Ensure valid values exist before scaling
                print("DEBUG: Ranking new user against full dataset PCA scores")

                # Transform all users' original feature data into PCA space
                features_no_cluster = df_aggregated.drop(columns=['id', 'Cluster'], errors='ignore')
                scaled_features = scaler.transform(features_no_cluster)
                pca_result_all_users = pca.transform(scaled_features)

                # Convert to DataFrame
                df_pca_all = pd.DataFrame(pca_result_all_users, columns=['PC1', 'PC2', 'PC3'])
                df_pca_all['Cluster'] = df_aggregated['Cluster']

                # Invert PC1 so lower values mean better scores
                df_pca_all['PC1_Inverted'] = -df_pca_all['PC1']

                # Add the new user's PCA values
                new_user_pca_df = pd.DataFrame([raw_pca_values], columns=['PC1', 'PC2', 'PC3'])
                new_user_pca_df['PC1_Inverted'] = -new_user_pca_df['PC1']

                # Concatenate new user PCA scores with all users
                df_pca_combined = pd.concat([df_pca_all, new_user_pca_df], ignore_index=True)

                # Apply MinMax Scaling across the full dataset (all users + new user)
                minmax_scaler = MinMaxScaler(feature_range=(0, 100))
                df_pca_combined_scaled = pd.DataFrame(
                    minmax_scaler.fit_transform(df_pca_combined[['PC1_Inverted', 'PC2', 'PC3']]),
                    columns=['PC1_Score', 'PC2_Score', 'PC3_Score']
                )

                # Extract the new user’s properly ranked PCA scores
                pca_values = df_pca_combined_scaled.iloc[-1].tolist()  # Last row is the new user

                print("DEBUG: Final PCA scores for new user (ranked properly):", pca_values)

            else:
                pca_values = [None, None, None]

            print("DEBUG: Final PCA values from precomputed centroids (0-100 scaled):", pca_values)

        # Update the user's profile with the new classification.
        profile.assigned_cluster = assigned_cluster
        profile.pca_values = pca_values
        profile.last_cluster_update = now()
        profile.save()
        print("DEBUG: Profile updated with assigned_cluster =", assigned_cluster,
              "and PCA values =", pca_values)

        return JsonResponse({
            'assigned_cluster': assigned_cluster,
            'pca_values': {
                "PC1": round(pca_values[0], 2) if pca_values[0] is not None else None,
                "PC2": round(pca_values[1], 2) if pca_values[1] is not None else None,
                "PC3": round(pca_values[2], 2) if pca_values[2] is not None else None,
            }
        })
    except Exception as e:
        print("DEBUG: Exception occurred:", str(e))
        return JsonResponse({'error': str(e)}, status=400)
##########################################################################################
##########################################################################################

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def classify_user_view(request):
    if request.method == 'POST':
        try:
            user = request.user  
            profile = Profile.objects.get(user=user)

            # Vérifier si la classification a déjà été faite cette semaine
            one_week_ago = now() - timedelta(days=7)
            if profile.last_cluster_update and profile.last_cluster_update >= one_week_ago:
                print("⏳ Chargement des données existantes...")
                return JsonResponse({
                    'assigned_cluster': profile.assigned_cluster,
                    'pca_values': profile.pca_values
                })

            # Récupérer les données Fitbit des 7 derniers jours
            one_week_ago = now() - timedelta(days=7)
            fitbit_records = FitbitDataHistory.objects.filter(user=user, date__gte=one_week_ago)

            if not fitbit_records.exists():
                return JsonResponse({'error': 'No Fitbit data found for the last 7 days'}, status=400)

            fitbit_df = pd.DataFrame.from_records(fitbit_records.values())

            #  Agréger les données
            aggregated_data = {
                "calories": fitbit_df["calories"].mean(),
                "distance": fitbit_df["distance"].mean(),
                "steps": fitbit_df["steps"].mean(),
                "lightly_active_minutes": fitbit_df["lightly_active_minutes"].mean(),
                "sedentary_minutes": fitbit_df["sedentary_minutes"].mean(),
                "age": profile.age if profile.age is not None else 0,
                "gender": 1 if profile.genre == "femme" else 0,
                "bmi": (profile.poids / (profile.taille ** 2)) if profile.poids and profile.taille else 0,
                "resting_hr": 55,
                "bpm": 65
            }

            new_user_df = pd.DataFrame([aggregated_data])

            #  Obtenir la classification + valeurs PCA
            assigned_clusters, new_user_pca = classify_new_users(new_user_df, scaler, pca, centroids_df, df_aggregated)
            assigned_cluster = int(assigned_clusters[0])
            pca_values = new_user_pca[0].tolist()

            print(f" Cluster assigné: {assigned_cluster}, PCA: {pca_values}")

            #  Stocker les données en base de données
            profile.assigned_cluster = assigned_cluster
            profile.pca_values = pca_values
            profile.last_cluster_update = now()
            profile.save()

            return JsonResponse({
                'assigned_cluster': assigned_cluster,
                'pca_values': pca_values
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    
    
    ################################################################################
    
    
    # health_app/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from health_app.groups import get_graph, get_group_members

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_members_view(request, user_id):
    """
    API endpoint that returns the list of very close-knit friends (group members)
    for the given user based on the friendship graph.
    """
    members = get_group_members(user_id)
    return Response({"user_id": user_id, "group_members": members})
