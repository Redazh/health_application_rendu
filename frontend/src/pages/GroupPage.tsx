import React, { useEffect, useState } from "react";
import { useParams, useHistory } from "react-router-dom";
import { IonPage, IonContent, IonHeader, IonTitle, IonToolbar, IonButton, IonList, IonItem, IonLabel, IonInput } from "@ionic/react";
import "./GroupPage.css";

const GroupPage: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // ID du groupe dans l'URL
  const history = useHistory();
  const [group, setGroup] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [newMember, setNewMember] = useState<string>("");
  const [newGroupName, setNewGroupName] = useState<string>("");
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  useEffect(() => {
    fetchGroupDetails();
  }, []);

  // Récupérer les détails du groupe
  const fetchGroupDetails = async () => {
    const token = localStorage.getItem("token");

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/groups/${id}/`, {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (!response.ok) {
        console.error("Erreur API:", response.status, await response.text());
        return;
      }

      const data = await response.json();
      setGroup(data);
      setMembers(data.members);
      setIsAdmin(data.is_admin);
    } catch (error) {
      console.error("Erreur de connexion:", error);
    }
  };

  // Ajouter un membre (uniquement un ami)
  const addMember = async () => {
    if (!newMember) {
      alert("Entrez un nom d'utilisateur !");
      return;
    }

    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/groups/add_member/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ group_id: id, username: newMember })
    });

    const data = await response.json();

    if (response.ok) {
      alert(`${newMember} ajouté au groupe !`);
      setNewMember("");
      fetchGroupDetails();
    } else {
      alert(data.error || "Vous ne pouvez ajouter que des amis dans ce groupe.");
    }
  };

  // Supprimer un membre (seulement si Admin)
  const removeMember = async (username: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/groups/remove_member/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ group_id: id, username })
    });

    if (response.ok) {
      alert(`${username} retiré du groupe !`);
      fetchGroupDetails();
    } else {
      alert("Erreur lors de la suppression.");
    }
  };

  // Supprimer le groupe (si Admin)
  const deleteGroup = async () => {
    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/groups/delete/", {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ group_id: id })
    });

    if (response.ok) {
      alert("Groupe supprimé !");
      history.push("/groups");
    } else {
      alert("Erreur lors de la suppression.");
    }
  };

  // Quitter le groupe (si membre simple)
  const leaveGroup = async () => {
    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/groups/leave/", {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ group_id: id })
    });

    if (response.ok) {
      alert("Vous avez quitté le groupe !");
      history.push("/groups");
    } else {
      alert("Erreur lors du départ.");
    }
  };

  // Renommer le groupe (seul l'Admin peut le faire)
  const renameGroup = async () => {
    if (!newGroupName) {
      alert("Veuillez entrer un nouveau nom !");
      return;
    }

    const token = localStorage.getItem("token");
    const response = await fetch("http://127.0.0.1:8000/api/groups/rename/", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ group_id: id, new_name: newGroupName })
    });

    const data = await response.json();

    if (response.ok) {
      alert("Groupe renommé avec succès !");
      setNewGroupName("");
      fetchGroupDetails();
    } else {
      alert(data.error || "Erreur lors du renommage.");
    }
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>{group?.name || "Groupe"}</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
  <div className="group-container">
    <div className="group-header">{group?.name || "Groupe"}</div>

    {/* Liste des membres */}
    <div className="members-list">
      <IonTitle>Membres</IonTitle>
      <IonList>
        {members.map((member, index) => (
          <IonItem key={index}>
            <IonLabel>{member.username}</IonLabel>
            {isAdmin && <IonButton color="danger" onClick={() => removeMember(member.username)}>❌</IonButton>}
          </IonItem>
        ))}
      </IonList>
    </div>

    {/* Ajouter un membre (si Admin) */}
    {isAdmin && (
      <>
        <IonInput className="group-input" value={newMember} placeholder="Nom du membre" onIonChange={(e) => setNewMember(e.detail.value!)} />
        <IonButton className="add-member-button" expand="full" onClick={addMember}>➕ Ajouter</IonButton>
      </>
    )}

    {/* Renommer le groupe (si Admin) */}
    {isAdmin && (
      <>
        <IonInput className="group-input" value={newGroupName} placeholder="Nouveau nom du groupe" onIonChange={(e) => setNewGroupName(e.detail.value!)} />
        <IonButton className="rename-button" expand="full" onClick={renameGroup}>✏️ Renommer Groupe</IonButton>
      </>
    )}

    {/* Supprimer le groupe (si Admin) */}
    {isAdmin && (
      <IonButton className="delete-button" expand="full" onClick={deleteGroup}>🗑 Supprimer Groupe</IonButton>
    )}

    {/* Quitter le groupe (si non Admin) */}
    {!isAdmin && <IonButton className="leave-button" expand="full" onClick={leaveGroup}>🚪 Quitter Groupe</IonButton>}

    {/* Retour à la liste des groupes */}
    <IonButton className="back-button" expand="full" onClick={() => history.push("/groups")}>🔙 Retour</IonButton>
  </div>
</IonContent>

    </IonPage>
  );
};

export default GroupPage;
