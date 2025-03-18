import React, { useState } from "react";
import { IonPage, IonContent, IonInput, IonButton, IonHeader, IonTitle, IonToolbar, IonItem, IonLabel, IonSelectOption, IonSelect } from "@ionic/react";
import { useHistory } from "react-router-dom";
import "./CompleteProfile.css"; // Import du CSS
import logo from "./logo.png"; 



const CompleteProfile: React.FC = () => {
  const [dateNaissance, setDateNaissance] = useState<string>("");
  const [poids, setPoids] = useState<number | null>(null);
  const [taille, setTaille] = useState<number | null>(null);
  const [objectif, setObjectif] = useState<number | null>(null);
  const [genre, setGenre] = useState<string | null>(null);
  const [profession, setProfession] = useState<string | null>(null);  // Ajout de la profession
  const [userGoal, setUserGoal] = useState<string | null>(null);  // Ajout de l'objectif utilisateur
  const [activitePhysique, setActivitePhysique] = useState<string | null>(null);
  const [compositionCorporelle, setCompositionCorporelle] = useState<string | null>(null);
  const [indicateursCardio, setIndicateursCardio] = useState<string | null>(null);
  const navigate = useHistory();

  const handleSubmit = async () => {
    if (!dateNaissance || poids === null || taille === null || objectif === null || !genre || !profession || !userGoal || !compositionCorporelle || !activitePhysique || !indicateursCardio) {
      alert("Veuillez remplir tous les champs !");
      return;
    }

    const token = localStorage.getItem("token");

    const response = await fetch("http://127.0.0.1:8000/api/user/complete-profile/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        date_naissance: dateNaissance,
        poids,
        taille,
        objectif_de_poids_quotidien: objectif,
        genre,
        profession,   // Ajout de la profession dans l'envoi au backend
        user_goal: userGoal,  // Ajout de l'objectif utilisateur
        activite_physique : activitePhysique,
        composition_corporelle : compositionCorporelle,
        indicateurs_cardio : indicateursCardio  
      }),
    });

    const data = await response.json();

    if (data.success) {
      alert("Profil complété avec succès !");
      const CLIENT_ID = "23Q39R";
      const REDIRECT_URI = "http://localhost:8100/callback2";

      window.location.href = `https://www.fitbit.com/oauth2/authorize?
        response_type=code
        &client_id=${CLIENT_ID}
        &redirect_uri=${encodeURIComponent(REDIRECT_URI)}
        &scope=activity%20profile%20sleep
        &prompt=login
        &expires_in=604800`.replace(/\s+/g, "");
    } else {
      alert(data.error || "Erreur lors de l'enregistrement.");
    }
  };

  return (
    <IonPage>
      <IonContent className="ion-padding">
      <div className="containerStyle">
      <div className="header-container">
        <img src={logo} alt="WellnessHub" className="logo" />
        <h2 className="greeting">Bonjour 👋</h2>
      </div>

      <div className="register-header">Compléter votre profil</div>
      <div className="register-form">
        {/* Genre */}
        <IonItem className="custom-select">
          <IonLabel>Genre</IonLabel>
          <IonSelect onIonChange={(e) => setGenre(e.detail.value)}>
            <IonSelectOption value="homme">Homme</IonSelectOption>
            <IonSelectOption value="femme">Femme</IonSelectOption>
          </IonSelect>
        </IonItem>

        {/* Profession */}
        <IonItem className="custom-select">
          <IonLabel>Profession</IonLabel>

            <IonSelect onIonChange={(e) => setProfession(e.detail.value)}>
              <IonSelectOption value="student">Étudiant</IonSelectOption>
              <IonSelectOption value="employee">Employé</IonSelectOption>
              <IonSelectOption value="self_employed">Indépendant / Freelance</IonSelectOption>
              <IonSelectOption value="business_owner">Entrepreneur</IonSelectOption>
              <IonSelectOption value="healthcare_worker">Professionnel de santé</IonSelectOption>
              <IonSelectOption value="teacher">Enseignant</IonSelectOption>
              <IonSelectOption value="athlete">Sportif</IonSelectOption>
              <IonSelectOption value="military">Militaire / Forces de l'ordre</IonSelectOption>
              <IonSelectOption value="unemployed">Sans emploi</IonSelectOption>
              <IonSelectOption value="retired">Retraité</IonSelectOption>
            </IonSelect>
          </IonItem>

          {/* Ajout du champ Objectif utilisateur */}
          <IonItem className="custom-select">
            <IonLabel>Objectif</IonLabel>

            <IonSelect onIonChange={(e) => setUserGoal(e.detail.value)}>
              <IonSelectOption value="lose_weight">Perte de poids</IonSelectOption>
              <IonSelectOption value="gain_muscle">Prendre du muscle</IonSelectOption>
              <IonSelectOption value="improve_endurance">Améliorer mon endurance</IonSelectOption>
              <IonSelectOption value="strengthen_body">Renforcer mon corps</IonSelectOption>
              <IonSelectOption value="increase_flexibility">Augmenter ma souplesse</IonSelectOption>
              <IonSelectOption value="improve_posture">Améliorer ma posture</IonSelectOption>
            </IonSelect>
          </IonItem>

          <IonInput className="register-input" type="date" placeholder="Date de naissance" onIonChange={(e) => setDateNaissance(e.detail.value!)} />
          <IonInput className="register-input" type="number" placeholder="Poids (kg)" onIonChange={(e) => setPoids(Number(e.detail.value))} />
          <IonInput className="register-input" type="number" placeholder="Taille (cm)" onIonChange={(e) => setTaille(Number(e.detail.value))} />
          <IonInput className="register-input" type="number" placeholder="Objectif de pas quotidien (pas)" onIonChange={(e) => setObjectif(Number(e.detail.value))} />
          
          <IonItem className="custom-select-container">
              <IonLabel className="custom-select-label">Activité Physique</IonLabel>
              <IonSelect onIonChange={(e) => setActivitePhysique(e.detail.value)}>
                <IonSelectOption value="A">Moins de 30 minutes</IonSelectOption>
                <IonSelectOption value="B">30-60 minutes</IonSelectOption>
                <IonSelectOption value="C">Plus de 60 minutes</IonSelectOption>
              </IonSelect>
            </IonItem>

            <IonItem className="custom-select-container">
              <IonLabel className="custom-select-label">Composition Corporelle</IonLabel>
              <IonSelect onIonChange={(e) => setCompositionCorporelle(e.detail.value)}>
                <IonSelectOption value="A">Haute graisse corporelle, faible dépense calorique</IonSelectOption>
                <IonSelectOption value="B">Composition moyenne, dépense calorique modérée</IonSelectOption>
                <IonSelectOption value="C">Mince/musclé avec une dépense calorique élevée</IonSelectOption>
              </IonSelect>
            </IonItem>

            <IonItem className="custom-select-container">
              <IonLabel className="custom-select-label">Indicateurs Cardio</IonLabel>
              <IonSelect onIonChange={(e) => setIndicateursCardio(e.detail.value)}>
                <IonSelectOption value="A">Fatigue rapide et essoufflement fréquent</IonSelectOption>
                <IonSelectOption value="B">Supportable mais un peu essoufflé après un moment</IonSelectOption>
                <IonSelectOption value="C">Facilement sans essoufflement</IonSelectOption>
              </IonSelect>
            </IonItem>

          <IonButton expand="full" className="register-button" onClick={handleSubmit}>
            Valider
          </IonButton>
        </div>
      </div>
      </IonContent>
    </IonPage>
  );
};

export default CompleteProfile;
