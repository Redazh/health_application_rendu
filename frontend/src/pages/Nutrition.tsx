import React from "react";
import { useLocation, useHistory } from "react-router-dom";
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonList, IonItem, IonLabel, IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonButton } from "@ionic/react";

// Interface pour le plan nutritionnel
interface Meal {
  meal_type: string;
  name: string;
  macros: {
    Calories: number;
    CarbohydrateContent: number;
    ProteinContent: number;
    FatContent: number;
  };
  ingredients: string[];
  instructions: string[];
}

// Interface pour `location.state`
interface LocationState {
  nutritionPlan?: Record<string, Meal>;
}

const Nutrition: React.FC = () => {
  const location = useLocation<LocationState>();
  const history = useHistory();
  const { nutritionPlan } = location.state || {};

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>🥗 Mon Plan Nutritionnel</IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent className="ion-padding">
        {nutritionPlan ? (
          <IonList>
            {Object.entries(nutritionPlan).map(([mealTime, meal]) => (
              <IonCard key={mealTime}>
                <IonCardHeader>
                  <IonCardTitle>🍽️ {meal.meal_type} - {meal.name}</IonCardTitle>
                </IonCardHeader>
                <IonCardContent>
                  <h3>📊 Macros</h3>
                  <p>🔥 Calories : {meal.macros.Calories} kcal</p>
                  <p>🍞 Glucides : {meal.macros.CarbohydrateContent} g</p>
                  <p>🍗 Protéines : {meal.macros.ProteinContent} g</p>
                  <p>🛢️ Lipides : {meal.macros.FatContent} g</p>

                  <h3>🛒 Ingrédients</h3>
                  <ul>
                    {meal.ingredients.map((ingredient, index) => (
                      <li key={index}>✔️ {ingredient}</li>
                    ))}
                  </ul>

                  <h3>👨‍🍳 Instructions</h3>
                  <ol>
                    {meal.instructions.map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ol>
                </IonCardContent>
              </IonCard>
            ))}
          </IonList>
        ) : (
          <IonItem>
            <IonLabel>🚫 Aucun plan nutritionnel disponible.</IonLabel>
          </IonItem>
        )}

        {/* Bouton retour */}
        <IonButton expand="full" color="primary" onClick={() => history.push("/dashboard")}>
          ⬅️ Retour à l'accueil
        </IonButton>
      </IonContent>
    </IonPage>
  );
};

export default Nutrition;
