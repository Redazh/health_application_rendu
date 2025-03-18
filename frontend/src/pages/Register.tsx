import React, { useState } from "react";
import { IonPage, IonContent, IonInput, IonButton, IonSelect, IonSelectOption, IonLabel,IonItem } from "@ionic/react";
import { useHistory } from "react-router-dom";
import { registerUser } from "../services/auth";
import "./Register.css"; 
import logo from "./logo.png"; 


const Register: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [dateNaissance, setDateNaissance] = useState<string>("");
  const [poids, setPoids] = useState<number | null>(null);
  const [taille, setTaille] = useState<number | null>(null);
  const [objectif, setObjectif] = useState<number | null>(null);
  const [genre, setGenre] = useState<string | null>(null); 
  const [profession, setProfession] = useState<string | null>(null);  // Ajout Profession
  const [otherProfession, setOtherProfession] = useState<string | null>(null);
  const [userGoal, setUserGoal] = useState<string | null>(null);  // Ajout Objectif utilisateur
  const [activitePhysique, setActivitePhysique] = useState<string | null>(null);
  const [compositionCorporelle, setCompositionCorporelle] = useState<string | null>(null);
  const [indicateursCardio, setIndicateursCardio] = useState<string | null>(null);
  const navigate = useHistory();

  const handleRegister = async () => {
    if (!username || !password || !dateNaissance || poids === null || taille === null || objectif === null || !genre || !profession || !userGoal || !compositionCorporelle || !activitePhysique || !indicateursCardio) {
      alert("Veuillez remplir tous les champs !");
      return;
    }

    const response = await registerUser(username, password, dateNaissance, poids, taille, objectif, genre, profession, userGoal, compositionCorporelle, activitePhysique, indicateursCardio);
    if (response.error) {
      alert(response.error);
    } else {
      alert("Inscription réussie !");
      const CLIENT_ID = "23Q39R";
    const REDIRECT_URI = "http://localhost:8100/callback2";

    window.location.href = `https://www.fitbit.com/oauth2/authorize?
      response_type=code
      &client_id=${CLIENT_ID}
      &redirect_uri=${encodeURIComponent(REDIRECT_URI)}
      &scope=activity%20profile%20sleep
      &prompt=login
      &expires_in=604800`.replace(/\s+/g, "");
      
    }
  };

  return (
    <IonPage>
      <IonContent className="ion-padding">
        <div className="containerStyle">
        <img src={logo} alt="WellnessHub" className="logoStyle" />
          <p className="subtitleStyle">Prenez soin de votre santé avec des recommandations intelligentes</p>
          <p className="titleStyle">Bienvenue sur WellnessHub</p>
          <div className="register-header">Inscription</div>
          <div style={{ padding: "20px" }}>

            <IonInput className="register-input" placeholder="Nom d'utilisateur" onIonChange={(e) => setUsername(e.detail.value!)} />
            <IonInput className="register-input" type="password" placeholder="Mot de passe" onIonChange={(e) => setPassword(e.detail.value!)} />
            
            <IonItem className="custom-select-container">
              <IonLabel className="custom-select-label">Genre</IonLabel>
              <IonSelect onIonChange={(e) => setGenre(e.detail.value)}>
                <IonSelectOption value="homme">Homme</IonSelectOption>
                <IonSelectOption value="femme">Femme</IonSelectOption>
              </IonSelect>
            </IonItem>
            <IonInput className="register-input" type="date" placeholder="Date de naissance" onIonChange={(e) => setDateNaissance(e.detail.value!)} />
            <IonInput className="register-input" type="number" placeholder="Poids (kg)" onIonChange={(e) => setPoids(Number(e.detail.value))} />
            <IonInput className="register-input" type="number" placeholder="Taille (cm)" onIonChange={(e) => setTaille(Number(e.detail.value))} />
            <IonInput className="register-input" type="number" placeholder="Objectif de pas quotidien (pas)" onIonChange={(e) => setObjectif(Number(e.detail.value))} />
            
            <IonItem className="custom-select-container">
              <IonLabel className="custom-select-label">Profession</IonLabel>
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
                {/*<IonSelectOption value="other">Autre</IonSelectOption>*/}
              </IonSelect>
            </IonItem>

            {/* Champ affiché uniquement si l'utilisateur sélectionne "Autre" 
            {profession === "other" && (
              <IonInput className="register-input" placeholder="Votre profession" onIonChange={(e) => setOtherProfession(e.detail.value!)} />
            )}
*/}
            {/* Ajout du champ Objectif utilisateur */}
            <IonItem className="custom-select-container">
              <IonLabel className="custom-select-label">Objectif</IonLabel>
              <IonSelect onIonChange={(e) => setUserGoal(e.detail.value)}>
                <IonSelectOption value="lose_weight">Perte de poids</IonSelectOption>
                <IonSelectOption value="gain_muscle">Prendre du muscle</IonSelectOption>
                <IonSelectOption value="improve_endurance">Améliorer mon endurance</IonSelectOption>
                <IonSelectOption value="strengthen_body">Renforcer mon corps</IonSelectOption>
                <IonSelectOption value="increase_flexibility">Augmenter ma souplesse</IonSelectOption>
                <IonSelectOption value="improve_posture">Améliorer ma posture</IonSelectOption>
              </IonSelect>
            </IonItem>

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
            
            <IonButton expand="full" className="register-button" onClick={handleRegister}>
              S'INSCRIRE
            </IonButton>
          </div>
        </div>
      </IonContent>
    </IonPage>
  );
};

export default Register;