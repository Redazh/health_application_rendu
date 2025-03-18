import React, { useEffect, useState } from "react";
import { IonPage, IonContent, IonHeader, IonTitle, IonToolbar, IonButton, IonList, IonItem, IonLabel, IonInput } from "@ionic/react";
import { useHistory } from "react-router-dom";
import "./Groups.css";
import profileIcon from "./profile.png"; 
import logo from "./logo.png"; 

const Groups: React.FC = () => {
  const [groups, setGroups] = useState<any[]>([]);
  const [groupName, setGroupName] = useState<string>("");
  const history = useHistory();

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/groups/list/", {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });
  
    const data = await response.json();
  
    console.log("Liste des groupes récupérée :", data); 
    setGroups(data);
  };
  

  const createGroup = async () => {
    if (!groupName) {
      alert("Veuillez entrer un nom de groupe !");
      return;
    }

    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/groups/create/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name: groupName })
    });

    if (response.ok) {
      alert("Groupe créé avec succès !");
      setGroupName("");
      fetchGroups(); // Rafraîchir la liste des groupes
    } else {
      alert("Erreur lors de la création du groupe.");
    }
  };

  return (
    <IonPage>
      <IonContent className="ion-padding">
  <div className="groups-container">
      <div className="header-container">
          <img src={logo} alt="WellnessHub" className="logo" />
          <img
            src={profileIcon}
            alt="Profil"
            className="profile-icon"
            onClick={() => history.push("/dashboard")} // Redirection au clic
          />
      </div>

    <div className="groups-header">Gérer mes Groupes</div>

    {/* Zone pour créer un nouveau groupe */}
    <IonInput
      className="groups-input"
      value={groupName}
      placeholder="Nom du groupe"
      onIonChange={(e) => setGroupName(e.detail.value!)}
    />
    <IonButton className="create-group-button" expand="full" onClick={createGroup}>
      ➕ Créer un groupe
    </IonButton>

    {/* Liste des groupes */}
    <div className="groups-list">
      <IonTitle>Mes Groupes</IonTitle>
      <IonList>
        {groups.length === 0 ? (
          <IonLabel>Aucun groupe pour le moment.</IonLabel>
        ) : (
          groups.map((group) => (
            <IonItem key={group.id} button onClick={() => history.push(`/group/${group.id}`)}>
              <IonLabel>{group.name}</IonLabel>
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

export default Groups;
