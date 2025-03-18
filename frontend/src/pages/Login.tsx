import React, { useState } from "react";
import { IonPage, IonContent, IonInput, IonButton, IonHeader, IonTitle, IonToolbar } from "@ionic/react";
import { useHistory } from "react-router-dom";
import { useGoogleLogin } from "@react-oauth/google";
import { loginUser } from "../services/auth";
import logo from "./logo.png"; 


const Login: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useHistory();

  // Connexion avec nom d'utilisateur et mot de passe
  const handleLogin = async () => {
    const response = await loginUser(username, password);
    if (response.access) {
      alert("Connexion réussie !");
      navigate.push("/dashboard");
    } else {
      alert(response.error || "Échec de la connexion.");
    }
  };
  
  

  // Connexion avec Google
  const loginWithGoogle = useGoogleLogin({
    flow: "auth-code",
    onSuccess: async (response) => {
      console.log("Auth Code:", response.code);

      const backendResponse = await fetch("http://127.0.0.1:8000/api/auth/google/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: response.code }),
      });

      const data = await backendResponse.json();
      
      if (data.access) {
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("token", data.access);
        localStorage.setItem("fitbit_token", data.fitbit_access_token);
        localStorage.setItem("fitbit_refresh_token", data.fitbit_refresh_token);
        alert("Connexion réussie !");
        if (data.is_new_user) {
          navigate.push("/complete-profile");
        } else {
          navigate.push("/dashboard");
        }
      } else {
        alert("Échec de la connexion Google.");
      }
    },
    onError: () => alert("Erreur d'authentification Google"),
  });

  return (
    <IonPage>
      <IonContent className="ion-padding" style={pageStyle}>
        <div style={containerStyle}>

          <img src={logo} alt="WellnessHub" style={logoStyle} />
          <p style={subtitleStyle}>Prenez soin de votre santé avec des recommandations intelligentes</p>


          <IonHeader>
              <div className="login-header" style={headerStyle}>Connexion</div>
          </IonHeader>
          <div style={{ padding: "20px" }}>
            {/* Champs Nom d'utilisateur et Mot de passe */}
            <IonInput
              style={inputStyle}
              placeholder="Nom d'utilisateur"
              onIonChange={(e) => setUsername(e.detail.value!)}
            />
            <IonInput
              style={inputStyle}
              type="password"
              placeholder="Mot de passe"
              onIonChange={(e) => setPassword(e.detail.value!)}
            />
            
            <IonButton expand="full" style={buttonStyle} onClick={handleLogin}>
              SE CONNECTER
            </IonButton>

            <IonButton expand="full" style={googleButtonStyle} onClick={() => loginWithGoogle()}>
              SE CONNECTER AVEC GOOGLE
            </IonButton>


            {/* Lien d'inscription */}
            <p style={linkStyle}>
              Pas encore de compte ?{" "}
              <a href="/register" style={{ color: "#00e600", fontWeight: "bold", textDecoration: "none" }}>
                S'inscrire
              </a>
            </p>

            <p style={linkStyle}>
              Nous collectons des informations personnelles pour améliorer votre expérience. Consultez notre {" "}
              <a href="/privacy-policy" style={{ color: "#4A90E2", textDecoration: "none" }}>
                Politique de confidentialité
              </a>
            </p>
          </div>
        </div>
      </IonContent>
    </IonPage>
  );
};


// Styles

const headerStyle = {
  background: "#00b300",
  color: "white",
  fontSize: "22px",
  padding: "5px",
  marginBottom: "10px",
 };

const pageStyle = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh",
  backgroundColor: "#f8f9fa",
};

const containerStyle = {
  width: "90%",
  maxWidth: "400px",
  backgroundColor: "#FFFFFF", 
  borderRadius: "15px",
  textAlign: "center" as const,
  padding: "30px",
  boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.1)", 
};


const inputStyle = {
  marginBottom: "15px",
  borderRadius: "5px",
  border: "1px solid #ccc",
  padding: "12px",
  width: "100%",
  fontSize: "16px",
  color: "#000", 
  backgroundColor: "#f5f5f5",
};

const buttonStyle = {
  backgroundColor: "#4A90E2 ",
  color: "white",
  borderRadius: "5px",
  fontSize: "16px",
  marginTop: "10px",
};

const googleButtonStyle = {
  backgroundColor: "#4A90E2 ",
  color: "white",
  borderRadius: "5px",
  fontSize: "16px",
  marginTop: "10px",
};

const linkStyle = {
  marginTop: "20px",
  fontSize: "12px",
  color: "#6B7280",
};


const logoStyle = {
  width: "120px",
  marginBottom: "10px",
};


const subtitleStyle = {
  fontSize: "14px",
  color: "#6B7280",
  marginBottom: "20px",
};

export default Login;
