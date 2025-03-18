import { useLocation } from "react-router-dom"; //  Import pour récupérer les données
import React, { useEffect, useState } from "react";
import { IonPage, IonContent, IonCard, IonCardContent, IonButton } from "@ionic/react";
import "./Workout.css";

const Workout: React.FC = () => {
  const location = useLocation();
  const [workoutData, setWorkoutData] = useState<any>(null);

  useEffect(() => {
    if (location.state && (location.state as any).workoutPlan) {
      setWorkoutData((location.state as any).workoutPlan);
    } else {
      console.error("Aucune donnée d'entraînement reçue.");
    }
  }, [location.state]);

  return (
    <div className="workout-container">
      <IonPage>
        <IonContent className="workout-container">
          {/* En-tête avec le logo */}
          <div className="workout-header">
            <h2 className="title">programme hebdomadaire</h2>
          </div>

          {/* Affichage du programme hebdomadaire */}
          {workoutData &&
            Object.entries(workoutData).map(([day, details]: any, index) => (
              <IonCard key={index} className="workout-day">
                <IonCardContent>
                  <h3 className="day-title">{day}</h3>

                  {details.collaborative ? (
                    // Display collaborative workout details if available
                    <div className="collaborative-workout">
                      <h4>Collaborative Workout</h4>
                      <p>
                        <strong>Group Exercise: </strong>
                        {details.collaborative.group_exercises.name}
                      </p>
                      <p>
                        <strong>Video: </strong>
                        <a
                          href={details.collaborative.group_exercises.video}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Watch Video
                        </a>
                      </p>
                      <p>
                        <strong>Participants: </strong>
                        {details.collaborative.participants.join(", ")}
                      </p>
                      <p>
                        <strong>Note: </strong>
                        {details.collaborative.note}
                      </p>
                    </div>
                  ) : (
                    // Otherwise, display the regular workout details
                    <>
                      <p className="warmup">
                        🔥 <strong>Échauffement :</strong> {details.warmUp}
                      </p>

                      <div className="exercise-list">
                        {details.exercises.map((exercise: any, i: number) => (
                          <div key={i} className="exercise">
                            <p className="exercise-name">🏃 {exercise.name}</p>
                            <p>
                              <strong>⏳ Durée:</strong> {exercise.duration}
                            </p>
                            {exercise.repetitions !== "-" && (
                              <p>
                                <strong>🔄 Répétitions:</strong> {exercise.repetitions}
                              </p>
                            )}
                            <p>
                              <strong>🔥 Calories brûlées:</strong> {exercise.caloriesBurned}
                            </p>
                          </div>
                        ))}
                      </div>

                      <p className="cooldown">
                        <strong>Récupération :</strong> {details.coolDown}
                      </p>
                      <p className="stress-management">
                        <strong>Gestion du stress :</strong> {details.stressManagement}
                      </p>
                    </>
                  )}
                </IonCardContent>
              </IonCard>
            ))}

          {/* Bouton Retour */}
          <IonButton expand="full" className="back-button" routerLink="/dashboard">
            🔙 Retour au Dashboard
          </IonButton>
        </IonContent>
      </IonPage>
    </div>
  );
};

export default Workout;
