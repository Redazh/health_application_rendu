import React, { useEffect, useState,useRef } from "react";
import { IonPage, IonContent, IonHeader, IonTitle, IonToolbar, IonCard, IonCardContent, IonButton, IonItem, IonLabel, IonRadio, IonRadioGroup,IonAlert } from "@ionic/react";

import { useHistory } from "react-router-dom";
import "./Dashboard.css";
import { IonIcon } from "@ionic/react";
import { arrowBack, arrowForward } from "ionicons/icons";

const Dashboard: React.FC = () => {
  const [userData, setUserData] = useState<any>(null);
  const [questions, setQuestions] = useState<{ question: string; options: string[] }[] | null>(null);
  const [responses, setResponses] = useState<{ [key: string]: string }>({});
  const [hasResponded, setHasResponded] = useState<boolean>(false);
  const [stressScore, setStressScore] = useState<number | null>(null);
  const [stressLevel, setStressLevel] = useState<string | null>(null);
  const [steps, setSteps] = useState<number | null>(null);
  const [distance, setDistance] = useState<number | null>(null);
  const [calories, setCalories] = useState<number | null>(null);
  const [sleepDuration, setSleepDuration] = useState<number | null>(null);
  const [sedentaryMinutes, setSedentaryMinutes] = useState<number | null>(null);
  const [lightlyActiveMinutes, setLightlyActiveMinutes] = useState<number | null>(null);
  const [fairlyActiveMinutes, setFairlyActiveMinutes] = useState<number | null>(null);
  const [veryActiveMinutes, setVeryActiveMinutes] = useState<number | null>(null);
  const [weeklySteps, setWeeklySteps] = useState<{ date: string, steps: number }[] | null>(null);
  const [classe, setclass] = useState<number | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]); // Default: today
  const [requiresFeedback, setRequiresFeedback] = useState(false);
  const [previousRecommendationId, setPreviousRecommendationId] = useState(null);
  const [workoutProgramId, setWorkoutProgramId] = useState(null);
  const [clusterId, setClusterId] = useState(null);
  const [feedbackRating, setFeedbackRating] = useState(3.5);
  const [cachedWorkoutPlan, setCachedWorkoutPlan] = useState(null);
  const ratingRef = useRef(feedbackRating); // Stocker la valeur temporairemen

   // Define the type for Fitbit historical data
    interface FitbitData {
      steps?: number;
      distance?: number;
      calories?: number;
      sleep_duration?: number;
      sedentary_minutes?: number;
      lightly_active_minutes?: number;
      fairly_active_minutes?: number;
      very_active_minutes?: number;
    }

    // Use the interface in the useState hook
    const [historicalData, setHistoricalData] = useState<FitbitData | null>(null);

  const history = useHistory();

  useEffect(() => {
    const fetchUserData = async () => {
      let token = localStorage.getItem("token");

      if (!token) {
        history.push("/login");
        return;
      }

      const response = await fetch("http://127.0.0.1:8000/api/user/profile/", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("fitbit_refresh_token");
        localStorage.removeItem("fitbit_token");
        localStorage.removeItem("fitbit_user_id");
        localStorage.removeItem("user_id");
        history.push("/login");
      } else {
        const data = await response.json();
        if (!data.error) {
          setUserData(data);
          setStressScore(data.stress_level); // Récupère le niveau de stress depuis l'API
          setStressLevel(
            data.stress_level === null
              ? "Non évalué"
              : data.stress_level <= 13
              ? "Faible stress"
              : data.stress_level <= 26
              ? "Stress modéré"
              : "Stress élevé"
          );
        }
      }
    };

    
    const fetchQuestionnaire = async () => {
      const token = localStorage.getItem("token");

      const response = await fetch("http://127.0.0.1:8000/api/questionnaire/", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      console.log("Questionnaire response:", response);
      const data = await response.json();

      if (data.message === "Questionnaire déjà rempli aujourd'hui.") {
        setHasResponded(true);
      } else {
        setQuestions(data.questions);
      }
    };

    const fetchFitbitData = async () => {
      const fitbitToken = localStorage.getItem("fitbit_token");

      if (fitbitToken) {
        console.log("Fitbit token found, synchronizing steps and distance...");
        await fetchStoredActivityData();
      } else {
        console.log("No Fitbit token found, user needs to reconnect.");
      }
    };

    fetchUserData();
    fetchFitbitData();
    fetchQuestionnaire();
  }, []);
 
  const changeDate = (days: number) => {
    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() + days);
    setSelectedDate(newDate.toISOString().split("T")[0]);
  };  
  const fetchStoredActivityData = async () => {
    let token = localStorage.getItem("token");
  
    if (!token) {
      console.log("⚠ No user token found.");
      return;
    }
  
    let response = await fetch("http://127.0.0.1:8000/api/fitbit/activity/", {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` },
    });
  
    const data = await response.json();
    if (data.data) {
      setSteps(data.data.steps);
      setSedentaryMinutes(data.data.minutesSedentary);
      setLightlyActiveMinutes(data.data.minutesLightlyActive);
      setFairlyActiveMinutes(data.data.minutesFairlyActive);
      setVeryActiveMinutes(data.data.minutesVeryActive);
      setCalories(data.data.calories);
      setDistance(data.data.distance);
      setSleepDuration(data.data.sleep_duration);
    } else {
      console.error("Failed to retrieve stored Fitbit data.");
    }
  };
  


  useEffect(() => {
    const fetchYesterdayData = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;
  
      const response = await fetch("http://127.0.0.1:8000/api/fitbit/fetch_yesterday/", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` },
      });
  
      const data = await response.json();
      if (data.message) {
        console.log("Yesterday's Fitbit data stored successfully:", data);
      } else {
        console.error("Error storing yesterday's Fitbit data:", data);
      }
    };
  
    fetchYesterdayData();

  }, []);

  const fetchHistoricalData = async () => {
    if (selectedDate === new Date().toISOString().split("T")[0]) {
      setHistoricalData(null); 
      return;
    }
  
    const token = localStorage.getItem("token");
    if (!token) return;
  
    const response = await fetch(`http://127.0.0.1:8000/api/fitbit/history/?date=${selectedDate}`, {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` },
    });
  
    const data = await response.json();
    if (!data.error) {
      setHistoricalData(data);
    } else {
      console.error("Error fetching FitbitDataHistory:", data.error);
      setHistoricalData(null); // Reset if no data found
    }
  };
  
  // Update data when selectedDate changes
  useEffect(() => {
    fetchHistoricalData();
  }, [selectedDate]);
  









  const fetchNutritionPlan = async () => {
    const token = localStorage.getItem("token");
    const userId = localStorage.getItem("user_id");
  
    if (!token || !userId) {
      console.error("Token ou ID utilisateur introuvable. Redirection vers login...");
      history.push("/login");
      return;
    }
  
    console.log("Token récupéré:", token);
    console.log("ID utilisateur récupéré:", userId);
  
    // Récupérer la dernière date de récupération du plan nutritionnel
    const lastFetched = localStorage.getItem(`lastNutritionFetch_${userId}`);
    const now = new Date();
    const todayDate = now.toISOString().split("T")[0]; // Récupère la date (YYYY-MM-DD)
  
    if (lastFetched) {
      const lastFetchedDate = lastFetched.split("T")[0]; // Récupère la date stockée sans l'heure
  
      if (lastFetchedDate === todayDate) {
        console.log("⏳ Plan nutritionnel déjà récupéré aujourd'hui. Chargement depuis le cache.");
        
        const cachedNutrition = localStorage.getItem(`nutritionPlan_${userId}`);
        if (cachedNutrition) {
          history.push({
            pathname: "/nutrition",
            state: { nutritionPlan: JSON.parse(cachedNutrition) },
          });
          return;
        }
      }
    }
  
    console.log("Envoi de la requête avec token:", token);
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/recommendation/", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
  
      const data = await response.json();
      console.log("Plan nutritionnel reçu:", data);
  
      if (data.success && data.meal_plan) {
        // Stocker la nouvelle date et le plan nutritionnel
        localStorage.setItem(`lastNutritionFetch_${userId}`, now.toISOString());
        localStorage.setItem(`nutritionPlan_${userId}`, JSON.stringify(data.meal_plan));
  
        history.push({
          pathname: "/nutrition",
          state: { nutritionPlan: data.meal_plan },
        });
      } else {
        console.error(" Réponse incorrecte :", data);
      }
    } catch (error) {
      console.error("Erreur lors de la récupération du plan nutritionnel :", error);
    }
  };

  const submitFeedback = async (rating: number) => {
    const token = localStorage.getItem("token");
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/update_rating/", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          recommendation_id: previousRecommendationId,
          rating: rating,
          workout_program_id: workoutProgramId,
          cluster_id: clusterId
        }),
      });
  
      const data = await response.json();
      if (data.success) {
        console.log("Feedback envoyé !");
        if (!requiresFeedback && cachedWorkoutPlan) {
          history.push({
            pathname: "/workout",
            state: { workoutPlan: cachedWorkoutPlan },
          });
        }
        setRequiresFeedback(false);
      } else {
        console.error("Erreur lors de l'envoi du feedback :", data.error);
      }
    } catch (error) {
      console.error("Erreur lors de la requête :", error);
    }
  };

  
  const fetchWorkoutPlan = async () => {
    const token = localStorage.getItem("token");
    const userId = localStorage.getItem("user_id"); //  Utilisation correcte de la clé "user_id"
  
    if (!token) {
      console.error("Token utilisateur introuvable. L'utilisateur doit se reconnecter.");
      history.push("/login");
      return;
    }
  
    if (!userId) {
      console.warn("user_id est introuvable dans localStorage, vérifie la connexion de l'utilisateur.");
      console.log("🛠 Contenu actuel de localStorage:", localStorage);
      return;
    }
  
    console.log("Token récupéré:", token);
    console.log("ID utilisateur récupéré:", userId);
  
    // Vérification de la dernière récupération du programme spécifique à l'utilisateur
    const lastFetched = localStorage.getItem(`lastWorkoutFetch_${userId}`);
    const now = new Date();
    const oneWeekInMs = 7 * 24 * 60 * 60 * 1000; // 7 jours en millisecondes
  
    if (lastFetched) {
      const lastFetchedDate = new Date(lastFetched);
  
      if (now.getTime() - lastFetchedDate.getTime() < oneWeekInMs) {
        console.log("⏳ Programme déjà récupéré récemment pour cet utilisateur.");
        const cachedWorkout = localStorage.getItem(`workoutPlan_${userId}`);
  
        if (cachedWorkout) {
          history.push({
            pathname: "/workout",
            state: { workoutPlan: JSON.parse(cachedWorkout) },
          });
          return;
        }
      }
    }
  
    console.log("📤 Envoi de la requête avec token:", token);
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/recommendation/", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
  
      const data = await response.json();
      console.log(" Recommandations reçues:", data);
  
      if (data.requires_feedback) {
        console.log("Feedback requis pour la recommandation précédente.");
        setRequiresFeedback(true);
        setPreviousRecommendationId(data.previous_recommendation_id);
        setWorkoutProgramId(data.workout_program_id);
        setClusterId(data.cluster_id);
      }
  
      if (data.success && data.workout_plan) {
        // Stocker les données en fonction de l'utilisateur
        localStorage.setItem(`lastWorkoutFetch_${userId}`, now.toISOString());
        localStorage.setItem(`workoutPlan_${userId}`, JSON.stringify(data.workout_plan));
        setCachedWorkoutPlan(data.workout_plan);
  
      } else {
        console.error("Réponse incorrecte :", data);
      }
    } catch (error) {
      console.error("Erreur lors de la récupération des recommandations :", error);
    }
  };
  
  
  
  const fetchClass = async () => {
    const userId = localStorage.getItem("user_id");
  
    if (!userId) {
      console.error(" User ID not found.");
      return;
    }
  
    const response = await fetch("http://127.0.0.1:8000/api/fitbit/classify/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id: userId }),
    });
  
    const data = await response.json();
    console.log("Classification response:", data);
    
    if (data.assigned_cluster !== undefined && data.pca_values) {
      setclass(data.assigned_cluster);
  
      // Ensure correct structure for PCA values
      const formattedPCA = {
        "Activity vs. Sedentary Lifestyle (PC1)": parseFloat(data.pca_values[0].toFixed(2)),
        "Body Metrics & Energy Expenditure (PC2)": parseFloat(data.pca_values[1].toFixed(2)),
        "Cardiovascular & Fitness Indicator (PC3)": parseFloat(data.pca_values[2].toFixed(2)),
    };
  
      history.push({
        pathname: "/class",
        state: { assignedCluster: data.assigned_cluster, pcaValues: formattedPCA },
      });
    } else {
      console.error("Failed to classify user or missing PCA values.");
    }
  };
  



  const handleResponseChange = (question: string, response: string) => {
    setResponses((prevResponses) => ({
      ...prevResponses,
      [question]: response,
    }));
    setSelectedAnswer(response);
  };

  const handleNextQuestion = () => {
    if (selectedAnswer) {
      setResponses((prevResponses) => ({
        ...prevResponses,
        [questions![currentQuestionIndex].question]: selectedAnswer,
      }));
      setSelectedAnswer(null);
      setCurrentQuestionIndex((prevIndex) => prevIndex + 1);
    }
  };

  const handleSubmit = async () => {
    const token = localStorage.getItem("token");

    const response = await fetch("http://127.0.0.1:8000/api/questionnaire/submit/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ responses }),
    });

    const data = await response.json();

    if (response.ok) {
      setHasResponded(true);
      setStressScore(data.stress_score); // Met à jour le score
      setStressLevel(data.stress_level); // Met à jour le niveau de stress
    }
  };


  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("fitbit_token");
    localStorage.removeItem("fitbit_refresh_token");
    localStorage.removeItem("fitbit_user_id");
    localStorage.removeItem("user_id");
    history.push("/login");
  };

  return (
    <IonPage>
      <IonContent className="ion-padding" style={pageStyle}>
        {hasResponded ? (
          userData && (
            <div style={containerStyle}>
              <IonHeader>
                    <div className="login-header" style={headerStyle}>Profil</div>
              </IonHeader>
  
              <IonCardContent>
                
                <div className="profile-info">
                  <p><strong>Nom d'utilisateur:</strong> {userData?.username}</p>
                  <p><strong>Genre:</strong> {userData?.genre ? userData.genre : "Non spécifié"}</p>
                  <p><strong>Poids:</strong> {userData?.poids} kg</p>
                  <p><strong>Taille:</strong> {userData?.taille} cm</p>
                  <p><strong>Objectif pas quotidien:</strong> {userData?.objectif_de_pas_quotidien} km</p>
                  <p><strong>Objectif utilisateur:</strong> {userData?.user_goal ? userData.user_goal : "Non spécifié"}</p>
                  <IonCard>
                    <IonCardContent>
                      <h3>Votre niveau de stress</h3>
                      <p><strong>Score :</strong> {stressScore !== null ? `${stressScore} / 40` : "Non évalué"}</p>  {/* Ajout de "/ 40" */}
                      <p><strong>Évaluation :</strong> {stressLevel}</p>
                    </IonCardContent>
                  </IonCard>

                  <IonCardContent>
  {/* Date Navigation */}
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
    <IonButton fill="clear" onClick={() => changeDate(-1)}> {/* Left Arrow */}
      <IonIcon icon={arrowBack} />
    </IonButton>
    
    <h3>{selectedDate === new Date().toISOString().split("T")[0] ? "Aujourd'hui" : selectedDate}</h3>

    <IonButton fill="clear" onClick={() => changeDate(1)} disabled={selectedDate === new Date().toISOString().split("T")[0]}>
      <IonIcon icon={arrowForward} /> {/* Right Arrow */}
    </IonButton>
  </div>

  {/* Display Data */}
  {selectedDate === new Date().toISOString().split("T")[0] ? (
    // Show today's data
    <>
      <p><strong>Nombre de pas:</strong> {steps !== null ? steps : "loading"}</p>
      <p><strong>Distance parcourue:</strong> {distance !== null ? `${distance} km` : "loading"}</p>
      <p><strong>Calories brûlées:</strong> {calories !== null ? `${calories} kcal` : "loading"}</p>
      <p><strong>Durée de sommeil:</strong> {sleepDuration !== null ? `${sleepDuration} heures` : "loading"}</p>
      <p><strong>Minutes Sédentaires:</strong> {sedentaryMinutes !== null ? `${sedentaryMinutes} min` : "loading"}</p>
      <p><strong>Minutes Légèrement Actives:</strong> {lightlyActiveMinutes !== null ? `${lightlyActiveMinutes} min` : "loading"}</p>
      <p><strong>Minutes Modérément Actives:</strong> {fairlyActiveMinutes !== null ? `${fairlyActiveMinutes} min` : "loading"}</p>
      <p><strong>Minutes Très Actives:</strong> {veryActiveMinutes !== null ? `${veryActiveMinutes} min` : "loading"}</p>
    </>
  ) : (
    // Show historical data from FitbitDataHistory
    historicalData ? (
      <>
        <p><strong>Nombre de pas:</strong> {historicalData.steps ?? "N/A"}</p>
        <p><strong>Distance parcourue:</strong> {historicalData.distance ? `${historicalData.distance} km` : "N/A"}</p>
        <p><strong>Calories brûlées:</strong> {historicalData.calories ? `${historicalData.calories} kcal` : "N/A"}</p>
        <p><strong>Durée de sommeil:</strong> {historicalData.sleep_duration ? `${historicalData.sleep_duration} heures` : "N/A"}</p>
        <p><strong>Minutes Sédentaires:</strong> {historicalData.sedentary_minutes ? `${historicalData.sedentary_minutes} min` : "N/A"}</p>
        <p><strong>Minutes Légèrement Actives:</strong> {historicalData.lightly_active_minutes ? `${historicalData.lightly_active_minutes} min` : "N/A"}</p>
        <p><strong>Minutes Modérément Actives:</strong> {historicalData.fairly_active_minutes ? `${historicalData.fairly_active_minutes} min` : "N/A"}</p>
        <p><strong>Minutes Très Actives:</strong> {historicalData.very_active_minutes ? `${historicalData.very_active_minutes} min` : "N/A"}</p>
      </>
    ) : (
      <p>⏳ Chargement des données...</p>
    )
  )}
</IonCardContent>

                </div>
                {requiresFeedback && (
                <IonAlert
                  isOpen={requiresFeedback}
                  onDidDismiss={() => setRequiresFeedback(false)}
                  header={"Évaluez votre programme précédent"}
                  message={"Veuillez donner une note entre 1 et 5 pour votre programme précédent."}
                  inputs={[
                    {
                      name: "rating",
                      type: "number",
                      min: 1,
                      max: 5,
                      value: feedbackRating,
                    },
                  ]}
                  buttons={[
                    {
                      text: "Annuler",
                      role: "cancel",
                      handler: () => setRequiresFeedback(false),
                    },
                    {
                      text: "Envoyer",
                      handler: (alertData) => {
                        console.log("🔹 Note envoyée:", alertData.rating);  
                        setFeedbackRating(Number(alertData.rating) || 3.5);  
                        submitFeedback(Number(alertData.rating)); 
                      },
                    },
                  ]}
                />
              )}
                <IonButton expand="full" style={buttonStyle} onClick={fetchWorkoutPlan}>
                  🏋️ Voir mon programme d'entraînement
                </IonButton>
                <IonButton expand="full" onClick={fetchNutritionPlan}>
                  🥗 Voir mon plan nutritionnel
                </IonButton>
                <IonButton expand="full" style={buttonStyle} onClick={() => history.push("/friends")}>
                    👥 Gérer mes amis
                  </IonButton>
                  <IonButton expand="full" style={buttonStyle} onClick={() => history.push("/groups")}>
                    📢 Gérer mes groupes
                  </IonButton>
                  <IonButton expand="full" style={buttonStyle} onClick={fetchClass}>
                      🔍 Voir mon cluster
                    </IonButton>

                    {classe !== null && (
                      <IonCard>
                        <IonCardContent>
                          <h3>Votre cluster : {classe}</h3>
                        </IonCardContent>
                      </IonCard>
                    )}
                <IonButton expand="full" style={logoutButtonStyle} onClick={handleLogout}>
                  🚪 Se Déconnecter
                </IonButton>
              </IonCardContent>
            </div>
          )
        ) : (
          <div style={containerStyle}>
            <IonCard>
              <IonCardContent>
                <h2 style={{ textAlign: "center", marginBottom: "20px" }}>Répondez au questionnaire</h2>
                {questions && questions.length > 0 ? (
                  <>
                    {/* Afficher une seule question à la fois */}
                    <IonLabel className="question-label">{questions[currentQuestionIndex].question}</IonLabel>
                    <IonRadioGroup onIonChange={(e) => handleResponseChange(questions[currentQuestionIndex].question,e.detail.value)} className="radio-group">
                      {questions[currentQuestionIndex].options.map((option, idx) => (
                        <IonItem key={idx} lines="none" className="radio-item">
                          <IonLabel>{option}</IonLabel>
                          <IonRadio slot="start" value={option} />
                        </IonItem>
                      ))}
                    </IonRadioGroup>

                    {/* Bouton "Suivant" ou "Envoyer" selon la question affichée */}
                    {currentQuestionIndex < questions.length - 1 ? (
                      <IonButton expand="full" color="primary" onClick={handleNextQuestion} disabled={!selectedAnswer}>
                        Suivant ➡
                      </IonButton>
                    ) : (
                      <IonButton expand="full" color="success" onClick={handleSubmit} disabled={!selectedAnswer}>
                        ✅ Envoyer
                      </IonButton>
                    )}
                  </>
                ) : (
                  <p>Chargement du questionnaire...</p>
                )}
              </IonCardContent>
            </IonCard>
          </div>
        )}
        </IonContent>
    </IonPage>
  );
  
};

const headerStyle = {
  background: "#581845",
  color: "white",
  fontSize: "22px",
  padding: "5px",
  marginBottom: "1px",
 };

const pageStyle = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh",
  backgroundColor: "#f8f9fa",
};

const containerStyle = {
  width: "400px",
  backgroundColor: "white",
  borderRadius: "10px",
  boxShadow: "0px 4px 10px #080808",
  textAlign: "center" as const,
  margin: "auto",
  padding: "20px",
};

const buttonStyle = { backgroundColor: "#581845", color: "white", marginTop: "10px" };
const logoutButtonStyle = { backgroundColor: "#c0392b", color: "white", marginTop: "10px" };


export default Dashboard;
