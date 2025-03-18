import React, { useEffect, useState } from "react";
import { IonPage, IonContent, IonHeader, IonTitle, IonToolbar, IonButton, IonInput, IonList, IonItem, IonLabel } from "@ionic/react";
import { useHistory } from "react-router-dom";
import "./Friends.css";
import profileIcon from "./profile.png"; 
import logo from "./logo.png"; 


const Friends: React.FC = () => {
  const [friends, setFriends] = useState<any[]>([]);
  const [pendingRequests, setPendingRequests] = useState<any[]>([]);
  const [suggestedFriends, setSuggestedFriends] = useState<any[]>([]);
  const [username, setUsername] = useState<string>("");
  const history = useHistory();

  // Charger la liste des amis, demandes en attente et suggestions
  useEffect(() => {
    fetchFriends();
    fetchPendingRequests();
    fetchSuggestedFriends();
  }, []);

  // Récupérer les amis acceptés
  const fetchFriends = async () => {
    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/friends/list/", {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });
    setFriends(await response.json());
  };

  // Récupérer les demandes en attente
  const fetchPendingRequests = async () => {
    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/friends/pending/", {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });
    setPendingRequests(await response.json());
  };

  const fetchSuggestedFriends = async () => {
    const token = localStorage.getItem("token");
  
    if (!token) {
      console.error("Aucun token trouvé. L'utilisateur est probablement déconnecté.");
      return;
    }
  
    try {
      const response = await fetch("http://127.0.0.1:8000/api/friends/suggestions/", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });
  
      if (!response.ok) {
        console.error("Erreur API:", response.status, await response.text());
        return;
      }
  
      const data = await response.json();
      console.log("Suggestions reçues:", data);
  
      setSuggestedFriends(data.length > 0 ? data : []);
    } catch (error) {
      console.error("Erreur de connexion:", error);
    }
  };
  

  // Envoyer une demande d'ami
  const sendFriendRequest = async (receiver?: string) => {
    const friendUsername = receiver || username;
    if (!friendUsername) {
      alert("Veuillez entrer un nom d'utilisateur !");
      return;
    }

    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/friends/request/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ receiver: friendUsername })
    });

    const data = await response.json();

    if (response.ok) {
      alert(`Demande envoyée à ${friendUsername} !`);
      setUsername("");
      fetchPendingRequests(); // Mettre à jour la liste des demandes en attente
      fetchSuggestedFriends(); // Mettre à jour la liste des suggestions
    } else {
      alert(data.error || "Erreur lors de l'envoi.");
    }
  };

  // Accepter une demande d'ami
  const acceptRequest = async (sender: string) => {
    const token = localStorage.getItem("token");
    await fetch("http://127.0.0.1:8000/api/friends/respond/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ sender, action: "accept" })
    });

    fetchPendingRequests();
    fetchFriends(); // Mettre à jour la liste des amis
  };

  // Refuser une demande d'ami
  const declineRequest = async (sender: string) => {
    const token = localStorage.getItem("token");
    await fetch("http://127.0.0.1:8000/api/friends/respond/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ sender, action: "decline" })
    });

    fetchPendingRequests();
  };

  // Supprimer un ami
  const removeFriend = async (friendUsername: string) => {
    const token = localStorage.getItem("token");
    await fetch("http://127.0.0.1:8000/api/friends/remove/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ friend: friendUsername })
    });

    fetchFriends();
  };

  return (
    <IonPage>
      <IonContent className="ion-padding">
        <div className="friends-container">

        <div className="header-container">
          <img src={logo} alt="WellnessHub" className="logo" />
          <img
            src={profileIcon}
            alt="Profil"
            className="profile-icon"
            onClick={() => history.push("/dashboard")} // Redirection au clic
          />
        </div>


        <div className="friends-header">Gérer mes Amis</div>

          {/* Ajouter un ami */}
          <IonInput
            className="friends-input"
            value={username}
            placeholder="Entrez un nom d'utilisateur"
            onIonChange={(e) => setUsername(e.detail.value!)}
          />
          <IonButton className="fr-button" expand="full" onClick={() => sendFriendRequest()}>
            ➕ Ajouter un ami
          </IonButton>

          {/* Suggestions d'amis */}
          <div className="friends-list">
            <IonTitle className="fr-title">Suggestions d'amis</IonTitle>
            <IonList>
              {suggestedFriends.length === 0 ? (
                <IonLabel>Aucune suggestion pour le moment</IonLabel>
              ) : (
                suggestedFriends.map((friend, index) => (
                  <IonItem key={index}>
                    <IonLabel>{friend.username}</IonLabel>
                    <IonButton color="primary" onClick={() => sendFriendRequest(friend.username)}>Ajouter</IonButton>
                  </IonItem>
                ))
              )}
            </IonList>
          </div>
          <div className="friends-list">
            <IonTitle className="fr-title">Demandes en attente</IonTitle>
            <IonList>
              {pendingRequests.length === 0 ? (
                <IonLabel>Aucune demande en attente</IonLabel>
              ) : (
                pendingRequests.map((request, index) => (
                  <IonItem key={index}>
                    <IonLabel>{request.username}</IonLabel>
                    <IonButton color="success" onClick={() => acceptRequest(request.username)}>Accepter</IonButton>
                    <IonButton color="danger" onClick={() => declineRequest(request.username)}>Refuser</IonButton>
                  </IonItem>
                ))
              )}
            </IonList>
          </div>
          {/* Liste des amis */}
          <div className="friends-list">
            <IonTitle className="fr-title">Mes amis</IonTitle>
            <IonList>
              {friends.length === 0 ? (
                <IonLabel>Vous n'avez pas encore d'amis</IonLabel>
              ) : (
                friends.map((friend, index) => (
                  <IonItem key={index}>
                    <IonLabel>{friend.username}</IonLabel>
                    <IonButton className="fr-button" onClick={() => removeFriend(friend.username)}>❌ Supprimer</IonButton>
                  </IonItem>
                ))
              )}
            </IonList>
          </div>

          
        </div>
      </IonContent>

    </IonPage>
  );
};

export default Friends;
