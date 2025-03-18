from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models import Q

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_groups")
    members = models.ManyToManyField(User, related_name="custom_groups", blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        """Calculate age dynamically based on birthdate."""
        if self.date_naissance:
            today = date.today()
            return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
        return None  # If no birthdate is provided
    def __str__(self):
        return self.name




class Friendship(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests_received")
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def get_friends(cls, user_id):
        """
        Returns a list of user IDs that are friends with the given user_id.
        Only friendships with status "accepted" are considered.
        """
        friendships = cls.objects.filter(
            Q(sender_id=user_id) | Q(receiver_id=user_id),
            status="accepted"
        )
        friend_ids = set()
        for friendship in friendships:
            if friendship.sender_id == user_id:
                friend_ids.add(friendship.receiver_id)
            else:
                friend_ids.add(friendship.sender_id)
        return list(friend_ids)
    class Meta:
        unique_together = ('sender', 'receiver')  # Empêche l'envoi de plusieurs demandes identiques

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_naissance = models.DateField(null=True, blank=True)
    poids = models.FloatField(null=True, blank=True)
    taille = models.FloatField(null=True, blank=True)
    objectif_de_pas_quotidien = models.FloatField(null=True, blank=True)
    genre = models.CharField(
        max_length=10,
        choices=[("homme", "Homme"), ("femme", "Femme")],
        null=True,
        blank=True
    )

    fitbit_access_token = models.TextField(null=True, blank=True)
    fitbit_user_id = models.CharField(max_length=255, null=True, blank=True)  # Stocker Fitbit User ID
    fitbit_refresh_token = models.TextField(null=True, blank=True)
    fitbit_token_expiry = models.DateTimeField(null=True, blank=True)
    stress_level = models.IntegerField(null=True, blank=True) 
    
    # Ajout du champ Profession
    PROFESSION_CHOICES = [
        ("student", "Étudiant"),
        ("employee", "Employé"),
        ("self_employed", "Indépendant / Freelance"),
        ("business_owner", "Entrepreneur"),
        ("healthcare_worker", "Professionnel de santé"),
        ("teacher", "Enseignant"),
        ("athlete", "Sportif"),
        ("military", "Militaire / Forces de l'ordre"),
        ("unemployed", "Sans emploi"),
        ("retired", "Retraité"),
    ]
    profession = models.CharField(max_length=50, choices=PROFESSION_CHOICES, null=True, blank=True)

    # Ajout du champ Objectif utilisateur
    USER_GOAL_CHOICES = [
        ("lose_weight", "Perte de poids"),
        ("gain_muscle", "Prendre du muscle"),
        ("improve_endurance", "Améliorer mon endurance"),
        ("strengthen_body", "Renforcer mon corps"),
        ("increase_flexibility", "Augmenter ma souplesse"),
        ("improve_posture", "Améliorer ma posture"),
    ]
    user_goal = models.CharField(max_length=50, choices=USER_GOAL_CHOICES, null=True, blank=True)
   

    # Nouveaux champs pour le mode de vie et les indicateurs de fitness
    activite_physique = models.CharField(
        max_length=50,
        choices=[("A", "Moins de 30 minutes"), ("B", "30-60 minutes"), ("C", "Plus de 60 minutes")],
        null=True,
        blank=True
    )
    composition_corporelle = models.CharField(
        max_length=50,
        choices=[("A", "Haute graisse corporelle, faible dépense calorique"),
                 ("B", "Composition moyenne, dépense calorique modérée"),
                 ("C", "Mince/musclé avec une dépense calorique élevée")],
        null=True,
        blank=True
    )
    indicateurs_cardio = models.CharField(
        max_length=50,
        choices=[("A", "Fatigue rapide et essoufflement fréquent"),
                 ("B", "Supportable mais un peu essoufflé après un moment"),
                 ("C", "Facilement sans essoufflement")],
        null=True,
        blank=True
    )
    
    assigned_cluster = models.IntegerField(null=True, blank=True)  # Ajout du cluster
    pca_values = models.JSONField(null=True, blank=True)  # Stockage des PCA
    last_cluster_update = models.DateTimeField(null=True, blank=True)  # Dernière mise à jour

    @property
    def age(self):
        """Calculate age dynamically based on birthdate."""
        if self.date_naissance:
            today = date.today()
            return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
        return None  # If no birthdate is provided
    def __str__(self):
        return self.user.username


class QuestionnaireResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    responses = models.JSONField()  # Stocke les réponses sous forme de JSON
    date = models.DateField(default=date.today)
    stress_score = models.IntegerField(null=True, blank=True)  # Nouveau champ pour le score de stress

    def __str__(self):
        return f"Réponses de {self.user.username} - {self.date} - Score: {self.stress_score}"

    


class FitbitData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    steps = models.IntegerField(default=0)
    sedentary_minutes = models.IntegerField(default=0)
    lightly_active_minutes = models.IntegerField(default=0)
    fairly_active_minutes = models.IntegerField(default=0)
    very_active_minutes = models.IntegerField(default=0)
    distance = models.FloatField(default=0.0)  # Distance en km
    calories = models.IntegerField(default=0)
    sleep_duration = models.FloatField(default=0.0)  # Durée en heures

    class Meta:
        unique_together = ('user', 'date')
        
    def __str__(self):
        return f"{self.user.username}"
    



class FitbitDataHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    steps = models.IntegerField(default=0)
    sedentary_minutes = models.IntegerField(default=0)
    lightly_active_minutes = models.IntegerField(default=0)
    fairly_active_minutes = models.IntegerField(default=0)
    very_active_minutes = models.IntegerField(default=0)
    distance = models.FloatField(default=0.0)  # Distance en km
    calories = models.IntegerField(default=0)
    sleep_duration = models.FloatField(default=0.0)  # Durée en heures

    class Meta:
        unique_together = ('user', 'date')

    def str(self):
        return f"{self.user.username}"
    

############# Rating System ################
############################################

class WorkoutProgram(models.Model):
    """
    Stocke un programme unique d'exercice basé sur un hash (sans tenir compte des jours).
    """
    hash = models.CharField(max_length=64, unique=True)  # Hash basé sur les exercices

    def __str__(self):
        return f"Workout Program {self.id}"


class UserWeeklyRecommendation(models.Model):
    """
    Stocke la recommandation de la semaine pour un utilisateur.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE)
    week_start = models.DateField()  # Date du lundi de la semaine de la recommandation
    recommendation_json = models.JSONField()  # Stocker la recommandation complète
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "week_start")  # Un utilisateur ne peut avoir qu'une recommandation par semaine


class WorkoutProgramClusterRating(models.Model):
    """
    Stocke la moyenne des ratings par cluster pour un programme spécifique.
    """
    workout_program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE)
    cluster_id = models.IntegerField()  # ID du cluster utilisateur
    avg_rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ("workout_program", "cluster_id")  # Évite les doublons

    def __str__(self):
        return f"Workout {self.workout_program.id} - Cluster {self.cluster_id} - Rating: {self.avg_rating} ({self.rating_count} ratings)"