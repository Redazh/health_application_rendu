import React from 'react';
import { IonPage, IonContent, IonButton, IonCard, IonCardHeader, IonCardTitle, IonCardContent,IonHeader,IonToolbar,IonTitle } from '@ionic/react';
import './Home.css';

const Home: React.FC = () => {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Fitbit App</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding" style={pageStyle}>
        <div style={containerStyle}>
          <h2 className="title">🏃‍♂️ Suivi Intelligent de votre Activité Physique</h2>
          <p className="subtitle">
            Analysez vos pas, suivez votre activité et recevez des recommandations personnalisées.
          </p>

          <IonCard className="info-card">
            <IonCardHeader>
              <IonCardTitle>🌟 Fonctionnalités principales</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              ✅ Suivi des pas et des calories brûlées 🔥<br />
              ✅ Analyse de votre activité quotidienne 📊<br />
              ✅ Recommandations basées sur vos objectifs 🎯<br />
              ✅ Historique et suivi des progrès 📅<br />
            </IonCardContent>
          </IonCard>

          <IonButton expand="full" className="glow-btn login-btn" routerLink="/login">🚀 Se Connecter</IonButton>
          <IonButton expand="full" className="glow-btn register-btn" routerLink="/register">✨ Créer un Compte</IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};

export default Home;

const pageStyle = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh",
  backgroundColor: "#f8f9fa",
};

const containerStyle = {
  width: "350px", // Même largeur que Login
  backgroundColor: "white", 
  borderRadius: "10px",
  boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)",
  textAlign: "center" as const,
  margin: "auto",
  padding: "30px",
};
