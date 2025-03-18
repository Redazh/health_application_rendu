import os
from groq import Groq

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from datasets import load_dataset
import random


from .ml_models import df_aggregated, scaler, pca, centroids_df
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

import re
import json

from datetime import datetime
import json
from health_app.groups import get_group_members, get_graph

############################# Workout recommendation #############################
###### WORKOUT COLLABORATIVE #################


"""_summary_
def get_group_members(user):

    Simulated version of get_group_members:
    For testing purposes, returns a list containing one friend with a similar fitness level.

    # For now, we simulate that every user has one friend with a similar fitness level.
    return ["Alice", "Bob"]
"""



def get_group_exercises(user, friends_list):
    """
    Retourne une liste d'exercices de groupe avec leurs liens vidéo YouTube,
    en fonction du niveau de fitness de l'utilisateur.
    
    Pour les utilisateurs avec un niveau 'low' ou 'sedentary', on propose des exercices légers.
    Pour 'moderate', on propose des exercices modérés.
    Pour 'high', des exercices plus intenses.
    
    Si le groupe compte plusieurs membres, un exercice collaboratif supplémentaire est ajouté.
    """
    fitness_level = user.get('fitness_level', 'moderate').lower()
    
    if fitness_level in ['low', 'sedentary']:
        exercises = [
            {"name": "Group Yoga", "video": "https://www.youtube.com/watch?v=CbyHvvW5l2g&ab_channel=mahiyogastudio"},
            {"name": "Gentle Stretching", "video": "https://www.youtube.com/watch?v=EvMTrP8eRvM&pp=ygUXR2VudGxlIFN0cmV0Y2hpbmcgY2xhc3M%3D"},
            {"name": "Walking Club", "video": "https://www.youtube.com/watch?v=dCjt9eptadI&ab_channel=Rickvanman-VarietyChannel"}
        ]
    elif fitness_level == 'moderate':
        exercises = [
            {"name": "Group HIIT", "video": "https://www.youtube.com/watch?v=JYfHiWN7gUQ&pp=ygUQR3JvdXAgSElJVCBjbGFzcw%3D%3D"},
            {"name": "Team Cardio", "video": "https://www.youtube.com/watch?v=rKf6YpYcb1s&pp=ygURVGVhbSBDYXJkaW8gY2xhc3M%3D"},
            {"name": "Outdoor Bootcamp", "video": "https://www.youtube.com/watch?v=rKf6YpYcb1s&pp=ygURVGVhbSBDYXJkaW8gY2xhc3M%3D"}
        ]
    elif fitness_level == 'high':
        exercises = [
            {"name": "Intense Group HIIT", "video": "https://www.youtube.com/watch?v=XGtjACeyHtc&pp=ygUSSW50ZW5zZSBHcm91cCBISUlU"},
            {"name": "Team Bootcamp", "video": "https://www.youtube.com/watch?v=XGtjACeyHtc&pp=ygUSSW50ZW5zZSBHcm91cCBISUlU"},
            {"name": "Sprint Intervals", "video": "https://www.youtube.com/watch?v=XGtjACeyHtc&pp=ygUSSW50ZW5zZSBHcm91cCBISUlU"}
        ]
    else:
        exercises = [
            {"name": "Group HIIT", "video": "https://www.youtube.com/watch?v=JYfHiWN7gUQ&pp=ygUQR3JvdXAgSElJVCBjbGFzcw%3D%3D"},
            {"name": "Team Cardio", "video": "https://www.youtube.com/watch?v=rKf6YpYcb1s&pp=ygURVGVhbSBDYXJkaW8gY2xhc3M%3D"},
            {"name": "Outdoor Bootcamp", "video": "https://www.youtube.com/watch?v=rKf6YpYcb1s&pp=ygURVGVhbSBDYXJkaW8gY2xhc3M%3D"}
        ]
        
    # Optionnel : si le groupe compte au moins 3 membres, ajouter un exercice collaboratif supplémentaire.
    if len(friends_list) >= 4:
        exercises.append({"name": "Team Relay Race", "video": "https://www.youtube.com/watch?v=dCjt9eptadI&ab_channel=Rickvanman-VarietyChannel"})
    
    return exercises


##############################################
def build_llm_prompt_rag_json(user):
    
    friends_list = get_group_members(user['user_id'])
    print("THE FRIENDS ARE \n")
    print(friends_list)
    """
    Génère un prompt détaillé pour LLaMA 3 en utilisant les insights du cluster de l'utilisateur,
    en incluant :
      - Les recommandations individuelles (workouts, calories brûlées, etc.)
      - Un plan hebdomadaire avec calculs des calories
      - Une invitation hebdomadaire à un workout collaboratif, le cas échéant.
    
    Si un groupe serré est détecté pour l'utilisateur, un jour aléatoire du plan hebdomadaire sera marqué
    comme collaboratif. Ce jour contiendra un sous-ensemble "collaborative" avec les détails de la session partagée.
    """
    # Obtenir les activités les plus pratiquées pour le cluster de l'utilisateur
    activities = get_activities_for_cluster(user['cluster_id'])
    print(f"Activités les plus pratiquées pour le Cluster {user['cluster_id']}: {activities}")
    
    # Calcul des calories brûlées par minute pour chaque activité du cluster de l'utilisateur
    calories_per_activity_cluster = {
        activity: estimate_calories_burned(activity, user['weight'], intensity=user['fitness_level'])
        for activity in activities
    }

    # Calcul des calories pour toutes les activités connues
    ALL_ACTIVITIES = [
        "cycling", "cardio", "hiit", "strength", "yoga", "running",
        "swimming", "hiking", "boxing", "martial arts"
    ]
    calories_per_all_activities = {
        activity: estimate_calories_burned(activity, user['weight'], intensity=user['fitness_level'])
        for activity in ALL_ACTIVITIES
    }

    # Générer un résumé des types de workout et calories brûlées pour le cluster de l'utilisateur
    workout_summary = "\n".join([
        f"- {activity.capitalize()}: ~{calories} kcal per minute"
        for activity, calories in calories_per_activity_cluster.items()
    ])

    # Générer un résumé des calories brûlées pour toutes les activités
    all_calories_summary = "\n".join([
        f"- {activity.capitalize()}: ~{calories} kcal per minute"
        for activity, calories in calories_per_all_activities.items()
    ])

    # Obtenir les workouts similaires en fonction du but de l'utilisateur
    similar_workouts = retrieve_similar_workouts(user['user_goal'])

    # Fonction locale pour calculer les calories totales en fonction de la durée
    def calculate_total_calories(activity_name, duration_minutes):
        calories_per_minute = calories_per_all_activities.get(activity_name.lower(), 0)
        return round(calories_per_minute * duration_minutes, 2)

    # Exemple de plan hebdomadaire avec calcul des calories
    weekly_plan = {
        "Monday": {
            "warmUp": "10 minutes of light stretching",
            "exercises": [
                {
                    "name": "Cycling",
                    "duration": 30,
                    "repetitions": "-",
                    "caloriesBurned": f"{calories_per_all_activities.get('cycling', 0)} * 30 = {calculate_total_calories('cycling', 30)}"
                },
                {
                    "name": "Strength Training",
                    "duration": 30,
                    "repetitions": "3 sets of 12-15 reps",
                    "caloriesBurned": f"{calories_per_all_activities.get('strength', 0)} * 30 = {calculate_total_calories('strength', 30)}"
                }
            ],
            "coolDown": "10 minutes of stretching",
            "stressManagement": "Deep breathing exercises before studying."
        },
        "Tuesday": {
            "warmUp": "10 minutes of mobility drills",
            "exercises": [
                {
                    "name": "Yoga",
                    "duration": 60,
                    "repetitions": "-",
                    "caloriesBurned": f"{calories_per_all_activities.get('yoga', 0)} * 60 = {calculate_total_calories('yoga', 60)}"
                }
            ],
            "coolDown": "5 minutes of meditation",
            "stressManagement": "Take a 10-minute walk outdoors between classes."
        }
    }

    # ----------------- Invitation au workout collaboratif -----------------
    # Récupérer la liste des amis proches (groupe serré) pour l'utilisateur
    # Cette fonction doit retourner une liste de noms (ex: ["Alice", "Bob", "Charlie"])
    friends_list = get_group_members(user['user_id'])

    if friends_list:
        # Sélectionner aléatoirement un jour de la semaine parmi ceux du plan
        collaborative_day = random.choice(list(weekly_plan.keys()))
        
        # Déterminer le type d'exercices pour le groupe (par exemple, en fonction du niveau moyen du groupe)
        # Implémentez cette fonction pour retourner une liste d'exercices adaptés (ex: ["HIIT", "Cardio"])
        group_exercises = get_group_exercises(user, friends_list)
        
        chosen_exercise = random.choice(group_exercises)

        # Extract just the exercise names for the invitation text        
        # Créer le bloc d'invitation collaborative
        collaborative_details = {
            "group_exercises": chosen_exercise,  # full details (names + video links)
            "participants": friends_list,
            "note": "This workout is a collaborative session shared with your group."
        }
        
        # Intégrer ces détails dans le jour sélectionné du plan hebdomadaire
        weekly_plan[collaborative_day]["collaborative"] = collaborative_details
        
        # Générer un texte d'invitation global (pour le prompt) en complément
        group_invitation_text = (
            f"Your group will have a collaborative workout session on {collaborative_day}.\n"
            f"Participants: {', '.join(friends_list)}.\n"
            f"Exercises: {', '.join(chosen_exercise['name'])}."
        )
    else:
        group_invitation_text = ""
    # -------------------------------------------------------------------------

    # Construction du prompt final
    prompt = f"""
    ### **User Information**
    - Age: {user['age']} years
    - Gender: {user['gender']}
    - Height: {user['height']} cm
    - Weight: {user['weight']} kg
    - Fitness Level: {user['fitness_level']}
    - Target Calories: {user['target_calories']} kcal per day
    - Workout Duration: {user['Workout Duration (mins)']} minutes per session
    - Job: {user['profession']}

    ### **Suggested Workouts Based on Similar Users (Calories per Workout per minute)**
    {workout_summary}

    ### **Estimated Calories Burned for All Activities**
    {all_calories_summary}

    ### **Workout Recommendations for Goal: {user['user_goal']}**
    {similar_workouts}

    ### **Collaborative Workout Invitation**
    {group_invitation_text}

    ### **Example Weekly Workout Plan with Calories Computed**
    ```json
    {weekly_plan}
    ```

    **Do not generate any extra text or explanations—return only the JSON response following this structure.**
    """

    return prompt



# Configuration de l'API Groq
client = Groq(
    api_key="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",
)


def generate_workout_plan_llama3(prompt):
    """
    Génère un plan d'entraînement avec LLaMA 3 via Groq.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a personal trainer AI."},
                  {"role": "user", "content": prompt}],
        max_tokens=10000
    )
    
    return response.choices[0].message.content

def estimate_calories_burned(activity: str, weight_kg: float, intensity: str = "moderate"):
    """
    Estime les calories brûlées par minute en fonction de l'activité, du poids et de l'intensité.
    
    Paramètres:
    - activity (str): Le sport pratiqué ("cycling", "cardio", "hiit", "strength", "yoga", "running").
    - weight_kg (float): Poids de l'utilisateur en kilogrammes.
    - intensity (str): Intensité de l'exercice ("low", "moderate", "high").
    
    Retourne:
    - float: Calories brûlées par minute.
    """
    # MET values from the Compendium of Physical Activities
    MET_VALUES = {
        "cycling": {"low": 4.0, "moderate": 7.0, "high": 10.0},
        "cardio": {"low": 4.5, "moderate": 6.5, "high": 9.0},
        "hiit": {"low": 6.0, "moderate": 10.0, "high": 14.0},
        "strength": {"low": 3.5, "moderate": 5.0, "high": 6.5},
        "yoga": {"low": 2.5, "moderate": 3.5, "high": 4.5},
        "running": {"low": 8.0, "moderate": 10.0, "high": 14.0},
        "swimming": {"low": 6.0, "moderate": 8.0, "high": 11.0},  # Ajouté pour cluster 6 (effort modéré, récupération)
        "hiking": {"low": 5.0, "moderate": 6.5, "high": 8.0},  # Ajouté pour cluster 3 (randonnée)
        "boxing": {"low": 5.0, "moderate": 9.0, "high": 12.0},  # Ajouté pour cluster 5 (effort explosif)
        "martial arts": {"low": 5.0, "moderate": 10.0, "high": 12.0}  # Ajouté pour cluster 5 (effort explosif)
    }
    
    if activity.lower() not in MET_VALUES:
        raise ValueError("Activité non reconnue. Choisissez parmi: 'cycling', 'cardio', 'hiit', 'strength', 'yoga', 'running'.")
    
    if intensity.lower() not in MET_VALUES[activity.lower()]:
        raise ValueError("Intensité non reconnue. Choisissez parmi: 'low', 'moderate', 'high'.")
    
    MET = MET_VALUES[activity.lower()][intensity.lower()]
    calories_per_minute = (MET * weight_kg * 3.5) / 200  # Formule standard des MET
    
    return round(calories_per_minute, 2)  # Arrondi à 2 décimales


def get_activities_for_cluster(cluster: int):
    """
    Retourne les activités les plus pratiquées en fonction du cluster identifié.

    Paramètre:
    - cluster (int): Numéro du cluster (1 à 6)

    Retourne:
    - list: Liste des activités les plus fréquentes dans ce cluster.
    """
    # Mapping des clusters aux activités les plus probables
    CLUSTER_ACTIVITIES = {
        1: ["running", "hiit"],  # Activité très intense avec distance élevée
        2: ["cycling", "cardio"],  # Effort modéré et constant
        3: ["yoga",  "cardio"],  # Activité modérée avec repos fréquent
        4: ["strength", "hiit"],  # Mix d’activité (musculation + HIIT)
        5: ["boxing", "martial arts", "hiit"],  # Effort explosif et intense
    }

    if cluster not in CLUSTER_ACTIVITIES:
        raise ValueError("Cluster non reconnu. Veuillez choisir un cluster entre 1 et 6.")

    return CLUSTER_ACTIVITIES[cluster]


def retrieve_similar_workouts(user_text, k=3):
    """
    Trouve les workouts les plus proches dans la base FAISS.
    """
    # Charger le dataset Hugging Face
    dataset = load_dataset("Kolibri753/generate-workouts")

    # Récupérer les descriptions de workouts
    workout_texts = [item["text"] for item in dataset["train"]]

    # Charger un modèle d'embedding optimisé
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Générer les embeddings des descriptions
    workout_embeddings = embedding_model.encode(workout_texts, convert_to_numpy=True)

    # Initialiser FAISS et indexer les embeddings
    dimension = workout_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(workout_embeddings)
    query_embedding = embedding_model.encode([user_text], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, k)
    
    return [workout_texts[i] for i in indices[0]]



############################# Recipe recommendation #############################



def calcul_besoins_energetiques(age, sexe, taille_m, poids_kg, niveau_sport):
    """
    Calcule les besoins énergétiques (MB et DEJ) d'un utilisateur avec la formule de Black et al. (1996).
    
    Args:
        date_naissance (str): Date de naissance au format "YYYY-MM-DD".
        sexe (str): "Male" ou "Female".
        taille_m (float): Taille en m.
        poids_kg (float): Poids en kilogrammes.
        niveau_sport (str): Niveau d'activité physique ("Sédentaire", "Actif léger", "Modéré", "Sportif", "Athlète").
    
    Returns:
        dict: Contient le Métabolisme de Base (MB) et la Dépense Énergétique Journalière (DEJ).
    """

    # # 1. Calcul de l'âge
    # annee_naissance = int(date_naissance.split("-")[0])
    # age = datetime.now().year - annee_naissance

    # 2. Calcul du MB selon la formule de Black et al. (1996)
    if sexe == "Male" :
        #Kcal = [1,083 x Poids(kg)0,48 x Taille(m)0,50 x Age(an)-0,13] x (1000/4,1855)
        MB = 1.083 * (poids_kg ** 0.48) * (taille_m ** 0.50) * (age ** -0.13) * (1000/4.1855)
    else :
        #Kcal = [0,963 x Poids(kg)0,48 x Taille(m)0,50 x Age(an)-0,13] x (1000/4,1855)
        MB = 0.963 * (poids_kg ** 0.48) * (taille_m ** 0.50) * (age ** -0.13) * (1000/4.1855)

    # 3. Facteurs d'Activité Physique (NAP)
    nap_levels = {
        "very low": 1.0,  #Sédentaire
        "low": 1.0, #Actif léger
        "moderate": 1.2,
        "high": 1.4
    }

    if niveau_sport not in nap_levels:
        raise ValueError("Le niveau de sport doit être : Sédentaire, Actif léger, Modéré ou Sportif")

    # 4. Calcul de la DEJ (Dépense Énergétique Journalière)
    DEJ = MB * nap_levels[niveau_sport]

    return {
        "Âge": age,
        "MB (kcal/jour)": round(MB, 2),
        "DEJ (kcal/jour)": round(DEJ, 2),
        "Niveau Sport": niveau_sport
    }


def repartir_calories(dej_total):
    """
    Répartit les calories totales sur la journée selon les proportions recommandées.

    Args:
        dej_total (float): Dépense énergétique journalière totale (kcal).

    Returns:
        dict: Répartition des calories sur les repas principaux et collations.
    """
    
    repartition = {
        "Breakfast": 0.25,   # 20 à 25 % des calories
        "Lunch": 0.40,       # 40 % des calories
        "Dinner": 0.30,      # 30 à 35 % des calories
        "Snack": 0.05        # 5 % des calories (facultatif)
    }

    calories_par_repas = {meal: round(dej_total * proportion) for meal, proportion in repartition.items()}
    
    return calories_par_repas


import pandas as pd

def repartition_macronutriments(calories_par_repas, activite):
    """
    Répartit les macronutriments (glucides, protéines, lipides) pour chaque repas
    selon l'objectif calorique et le type d'activité de l'utilisateur.
    
    Paramètres :
    - calories_par_repas (dict) : Calories par repas (ex: {'Breakfast': 625, 'Lunch': 1000, ...})
    - activite (str) : Type d'activité ("sédentaire", "endurance", "force")

    Retourne :
    - dict contenant la répartition des macronutriments par repas
    """

    # Définition des pourcentages selon l'activité
    repartition = {
        "sédentaire": {"Glucides": (0.50, 0.55), "Protéines": (0.15, 0.15), "Lipides": (0.30, 0.35)},
        "endurance": {"Glucides": (0.60, 0.70), "Protéines": (0.15, 0.15), "Lipides": (0.15, 0.25)},
        "force": {"Glucides": (0.55, 0.60), "Protéines": (0.20, 0.20), "Lipides": (0.20, 0.25)}
    }

    if activite not in repartition:
        raise ValueError("Type d'activité non valide. Choisissez parmi : 'sédentaire', 'endurance', 'force'")

    # Sélection des pourcentages
    macros = repartition[activite]

    # Calcul de la répartition pour chaque repas
    repas_macros = {}
    for repas, calories in calories_par_repas.items():
        repas_macros[repas] = {
            "Calories": calories,
            "CarbohydrateContent": round((calories * sum(macros["Glucides"]) / 2) / 4, 1),
            "ProteinContent": round((calories * sum(macros["Protéines"]) / 2) / 4, 1),
            "FatContent": round((calories * sum(macros["Lipides"]) / 2) / 9, 1)
        }
    
    df_macros = pd.DataFrame.from_dict(repas_macros, orient="index")

    df_macros['Cal_glucides'] = df_macros['CarbohydrateContent'] * 4
    df_macros['Cal_proteines'] = df_macros['ProteinContent'] * 4
    df_macros['Cal_lipides'] = df_macros['FatContent'] * 9
    df_macros['calories_calculees'] = df_macros['Cal_glucides'] +  df_macros['Cal_proteines'] + df_macros['Cal_lipides']


    # Calcul des pourcentages par rapport aux calories totales
    df_macros['pct_glucides'] = (df_macros['Cal_glucides'] / df_macros['calories_calculees']) * 100
    df_macros['pct_proteines'] = (df_macros['Cal_proteines'] / df_macros['calories_calculees']) * 100
    df_macros['pct_lipides'] = (df_macros['Cal_lipides'] / df_macros['calories_calculees']) * 100

    resultats_macros_new = df_macros.to_dict(orient='index')
    return df_macros,resultats_macros_new


def find_best_meals_knn(nutrition_needs, df_meals, k_neighbors=5):
    """
    Trouve les meilleurs repas en utilisant KNN après un filtrage sur la catégorie et les calories.

    Params:
    - nutrition_needs (dict) : Besoins par repas {'Breakfast': {'Calories': X, 'CarbohydrateContent': Y, ...}, ...}
    - df_meals (DataFrame) : Base de données des repas
    - k_neighbors (int) : Nombre de voisins à considérer dans KNN

    Retourne:
    - Dict avec les meilleures recommandations par catégorie
    """
    recommendations = {}

    for meal_type, needs in nutrition_needs.items():
        # Filtrer les repas qui correspondent au bon type de repas
        if meal_type == "Dinner" or meal_type == "Lunch" :
            filtered_df = df_meals[(df_meals["MealCategory"] == "Dinner") | (df_meals["MealCategory"] == "Lunch")]
        else : 
            filtered_df = df_meals[df_meals["MealCategory"] == meal_type]

        if filtered_df.empty:
            print(f"Aucun repas trouvé pour {meal_type}")
            continue

        # Filtrer les repas proches en calories (+/- 15% autour des besoins)
        # cal_min = needs["Calories"] * 0.85
        # cal_max = needs["Calories"] * 1.15
        # filtered_df = filtered_df[(filtered_df["Calories"] >= cal_min) & (filtered_df["Calories"] <= cal_max)]

        if filtered_df.empty:
            print(f"Aucun repas avec des calories proches pour {meal_type}")
            continue

        # Appliquer KNN sur les macronutriments (glucides, protéines, lipides)
        meal_features = filtered_df[["pct_glucides", "pct_proteines", "pct_lipides"]].values

        target_vector = np.array([
            needs["pct_glucides"], 
            needs["pct_proteines"], 
            needs["pct_lipides"]
        ]).reshape(1, -1)

        knn = NearestNeighbors(n_neighbors=min(k_neighbors, len(filtered_df)), metric="euclidean")
        knn.fit(meal_features)

        distances, indices = knn.kneighbors(target_vector)
        top_meals = filtered_df.iloc[indices[0]]

        # Stocker les résultats
        recommendations[meal_type] = top_meals

    return recommendations


def generate_recipe_adaptation(prompt):
    """
    Generates an adapted recipe using LLaMA 3 via Groq.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a culinary expert who adjusts recipes to meet specific nutritional needs."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10000
    )
    
    return response.choices[0].message.content

def build_adaptation_prompt(meal_type, rec_recipe, macro_needs):
    """
    Builds a structured JSON prompt for adapting a recipe to the user's calorie needs.

    Parameters:
      - meal_type (str): Type of meal (e.g., "Dinner").
      - rec_recipe (Series): A row from the recommendations DataFrame containing the recipe.
      - macro_needs (dict): The user's nutritional needs for this meal, e.g.,
        {'Calories': 750, 'CarbohydrateContent': ..., 'ProteinContent': ..., 'FatContent': ...}

    Returns:
      - A clear prompt instructing the LLM to return a JSON object with:
        - meal_type: The type of meal (Breakfast, Lunch, Dinner, etc.)
        - name: Adapted recipe name
        - calories: Adjusted total calories
        - macros: Adjusted carbohydrate, protein, and fat content
        - ingredients: List of ingredients with adjusted **realistic** quantities (not fractional units)
        - instructions: Reformatted cooking instructions adapted to the new ingredient amounts
        - photo: URL of the recipe image (if available)

    """
    original_calories = rec_recipe['Calories']
    original_servings = rec_recipe['RecipeServings']
    desired_calories = macro_needs['Calories']

    # Calculate the scaling factor
    scaling_factor = desired_calories / original_calories
    adjusted_servings = original_servings * scaling_factor

    # Adjust nutritional values manually
    adjusted_macros = {
        "Calories": round(desired_calories, 1),
        "CarbohydrateContent": round(rec_recipe['CarbohydrateContent'] * scaling_factor, 1),
        "ProteinContent": round(rec_recipe['ProteinContent'] * scaling_factor, 1),
        "FatContent": round(rec_recipe['FatContent'] * scaling_factor, 1)
    }

    prompt = (
        f"You are a culinary expert responsible for adjusting recipes based on user calorie needs. "
        f"Your task is to scale down or up the given recipe and provide a structured JSON output. "
        f"Make sure the ingredient measurements remain **realistic** (e.g., instead of '0.62 onion', write '1/2 onion').\n\n"
        f"### **Recipe Scaling Calculation**\n"
        f"- Original Recipe: {rec_recipe['Name']}\n"
        f"- Original Servings: {original_servings}\n"
        f"- Original Calories: {original_calories}\n"
        f"- Desired Calories: {desired_calories}\n"
        f"- Scaling Factor = {scaling_factor:.3f}\n"
        f"- Adjusted Servings = {adjusted_servings:.1f}\n\n"
        
        f"### **Nutritional Values After Scaling**\n"
        f"- Calories: {adjusted_macros['Calories']} kcal\n"
        f"- Carbohydrates: {adjusted_macros['CarbohydrateContent']} g\n"
        f"- Proteins: {adjusted_macros['ProteinContent']} g\n"
        f"- Fats: {adjusted_macros['FatContent']} g\n\n"

        f"### **Required JSON Output Format**\n"
        f"Respond with a well-formatted JSON object containing:\n"
        f"```json\n"
        f"{{\n"
        f'  "meal_type": "{meal_type}",\n'
        f'  "name": "{rec_recipe["Name"]} (Adapted for {desired_calories} Calories)",\n'
        f'  "macros": {json.dumps(adjusted_macros)},\n'
        f'  "ingredients": [\n'
        f'    Adjust the original ingredients from: {rec_recipe["RecipeIngredientParts"]}.\n'
        f'    Multiply by the scaling factor ({scaling_factor:.3f}) and convert the amounts into practical values.\n'
        f'    Example: Instead of "0.62 onion", say "1/2 onion".\n'
        f'  ],\n'
        f'  "instructions": [\n'
        f'    Rewrite the cooking steps from: {rec_recipe["RecipeInstructions"]}.\n'
        f'    Adjust wording based on the new ingredient amounts.\n'
        f'  ],\n'
        f"}}\n"
        f"```\n\n"
        f"**Important:**\n"
        f"- Do not return a long explanation, just return a clean JSON object."
    )
    return prompt



def extract_json_from_text(text):
    """
    Extrait le JSON valide d'une réponse contenant du texte supplémentaire.

    Args:
        text (str): Texte contenant potentiellement un JSON.

    Returns:
        str: Le JSON extrait ou None si aucun JSON valide trouvé.
    """
    match = re.search(r'\{.*\}', text, re.DOTALL)  # Cherche un bloc JSON entre { }
    if match:
        return match.group(0)  # Retourne uniquement le JSON trouvé
    return None  # Retourne None si aucun JSON n'est trouvé

def get_recipe_recommendation(user,json_workout):
    """
    Génère une recommandation de repas adaptée aux besoins nutritionnels de l'utilisateur pour toute la journée.
    
    Paramètres:
    - user (dict): Informations de l'utilisateur (âge, genre, poids, taille).
    - niveau_sport (str): Niveau d'activité physique.
    - activite (str): Type d'activité ("sédentaire", "endurance", "force").

    Retourne:
    - dict contenant les recettes adaptées pour tous les repas de la journée.
    """

    # Load your dataset
    import os

    # Récupérer le répertoire du script en cours d'exécution
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construire le chemin relatif vers le fichier CSV
    csv_path = os.path.join(script_dir, "recipes_cleaned.csv")

    # Charger le fichier
    df_recipes = pd.read_csv(csv_path)

    # Calcul des besoins énergétiques de l'utilisateur
    user_info = calcul_besoins_energetiques(user['age'], user['gender'], user['height']/100, user['weight'], user['fitness_level'])

    calories_par_repas = repartir_calories(user_info["DEJ (kcal/jour)"])

    # Calcul de la répartition des macronutriments pour chaque repas
    today = datetime.today().strftime('%A')
    activite = determine_activity_type(json_workout, today)
    df_macros, resultats_macros_new = repartition_macronutriments(calories_par_repas, activite)

    # Trouver les meilleurs repas pour chaque moment de la journée
    recommendations = find_best_meals_knn(resultats_macros_new, df_recipes, k_neighbors=7)

    # Générer une recette adaptée pour chaque repas
    daily_meal_plan = {}

    for meal_type in ["Breakfast", "Lunch", "Dinner", "Snack"]:
        if meal_type in recommendations and not recommendations[meal_type].empty:

            # Sélectionner un indice aléatoire parmi les repas disponibles
            random_index = random.randint(0, len(recommendations[meal_type]) - 1)
            rec_recipe = recommendations[meal_type].iloc[random_index]

            macro_needs = resultats_macros_new[meal_type]

            # Générer le prompt pour adapter la recette
            adaptation_prompt = build_adaptation_prompt(meal_type, rec_recipe, macro_needs)

            # Générer la recette adaptée via LLaMA 3
            adapted_recipe = generate_recipe_adaptation(adaptation_prompt)

            # Ajouter la recette adaptée au plan de repas
            daily_meal_plan[meal_type] = json.loads(extract_json_from_text(adapted_recipe))  # Convertir le JSON généré en dict

    # Afficher le plan de repas sous forme JSON
    meal_plan_text = json.dumps(daily_meal_plan, indent=4)

    return daily_meal_plan,meal_plan_text


def determine_activity_type(json_workout, jour):
    """
    Détermine le type d'activité dominant pour une journée donnée à partir de json_workout.

    Paramètres:
    - json_workout (dict) : Plan d'entraînement structuré (exercices par jour).
    - jour (str) : Jour de la semaine (ex: "Monday", "Tuesday", ...).

    Retourne:
    - str : Type d'activité dominant ("sédentaire", "force", "endurance").
    """
    # Vérifier si la journée existe dans json_workout
    if jour not in json_workout:
        raise ValueError(f"Jour '{jour}' non trouvé dans json_workout.")

    # Liste des exercices pratiqués ce jour-là
    exercices = [ex["name"].lower() for ex in json_workout[jour]["exercises"]]

    # Définition des catégories d'activités
    ACTIVITES_FORCE = {"strength training", "weightlifting", "powerlifting"}
    ACTIVITES_ENDURANCE = {"running", "cycling", "swimming", "hiit", "hiking", "cardio", "boxing", "martial arts"}
    ACTIVITES_SEDENTAIRE = {"yoga", "stretching", "meditation"}

    # Analyse des exercices pour déterminer l'activité dominante
    if any(ex in ACTIVITES_ENDURANCE for ex in exercices):
        return "endurance"
    elif any(ex in ACTIVITES_FORCE for ex in exercices):
        return "force"
    elif all(ex in ACTIVITES_SEDENTAIRE for ex in exercices):  # Vérifie si tous sont sédentaires
        return "sédentaire"
    return "sédentaire"  



def get_workout_recommendation(user):
    """
    Génère une recommandation d'entraînement adaptée aux besoins de l'utilisateur.
    """
    # Générer le prompt avec RAG
    llm_prompt_rag = build_llm_prompt_rag_json(user)
    llm_prompt_rag += "\n\nEnsure the output is strictly valid JSON format with all keys and string values enclosed in double quotes (\")."
    # Générer le programme avec LLaMA 3 via Groq
    workout_plan_text = generate_workout_plan_llama3(llm_prompt_rag)

    json_workout = json.loads(extract_json_from_text(workout_plan_text))



    return json_workout, workout_plan_text

def record_workout_completion(user_data, recommendation, baseline_calories):
    """
    Compare l'activité réelle d'un utilisateur avec la recommandation prévue pour la journée,
    en tenant compte des calories brûlées hors sport.
    
    :param user_data: dict contenant les données journalières (calories, minutes actives, steps, distance)
    :param recommendation: dict contenant la recommandation du jour
    :param baseline_calories: estimation des calories brûlées sans sport (métabolisme basal + activité normale)
    :return: score d'adhérence (0 à 100%)
    """
    # Extraire les données utilisateur
    calories_burned = user_data.get("calories", 0)
    minutes_active = user_data.get("minutes_active", 0)

    
    # Calcul des calories réellement liées au sport
    sport_calories = max(calories_burned - baseline_calories,0)  # Ne pas avoir de valeurs négatives

    
    # Extraire la recommandation
    expected_calories = sum([eval(exo["caloriesBurned"].split('=')[0]) for exo in recommendation["exercises"]]) ## t9ra dikchi li mora egal
    expected_minutes = sum([exo["duration"] for exo in recommendation["exercises"]])
    
    # Calculer le score basé sur les calories (corrigé)
    calorie_ratio = min(sport_calories / expected_calories, 1)  # Max 100%
    minutes_ratio = min(minutes_active / expected_minutes, 1)  # Max 100%
    
    
    # Pondération des scores
    adherence_score = (calorie_ratio * 0.5 + minutes_ratio * 0.5) * 100
    
    print(round(adherence_score, 2))
    return 1 if round(adherence_score, 2) > 70 else 0


def infer_values_from_cluster_v2(user):
    """
    Met à jour uniquement les valeurs manquantes de l'utilisateur à partir des données de son cluster.

    Paramètres:
    - user (dict): Dictionnaire contenant les informations de l'utilisateur, y compris 'cluster_id'.

    Retourne:
    - user (dict) mis à jour avec les valeurs moyennes déduites.
    """
    cluster_id = user["cluster_id"]
    
    # Filtrer le DataFrame pour obtenir les données du cluster correspondant
    cluster_data = df_aggregated[df_aggregated["Cluster"] == cluster_id]
    
    if cluster_data.empty:
        raise ValueError(f"Aucune donnée trouvée pour le cluster {cluster_id}. Vérifiez les données agrégées.")
    
    # Mettre à jour uniquement les champs demandés
    user["target_calories"] = round(cluster_data["calories"].mean(), 1)
    
    # Déterminer le niveau de fitness
    avg_very_active = cluster_data["very_active_minutes"].mean()
    avg_moderately_active = cluster_data["moderately_active_minutes"].mean()

    if avg_very_active > 90:
        fitness_level = "high"
    elif avg_moderately_active > 60 or avg_very_active > 60:
        fitness_level = "moderate"
    else:
        fitness_level = "low"

    user["fitness_level"] = fitness_level

    # Définir la durée d'entraînement en fonction du niveau de fitness
    fitness_duration_mapping = {
        "low": 30,
        "moderate": 50,
        "high": 75
    }
    user["Workout Duration (mins)"] = fitness_duration_mapping[fitness_level]

    return user