const API_URL = "http://127.0.0.1:8000/api/";
export const registerUser = async (
  username: string,
  password: string,
  dateNaissance: string,
  poids: number,
  taille: number,
  objectif: number,
  genre: string,
  profession: string, 
  userGoal: string,
  activitePhysique: string,
  compositionCorporelle: string,
  indicateursCardio: string  
) => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/register/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        password,
        date_naissance: dateNaissance,
        poids,
        taille,
        objectif_de_pas_quotidien: objectif,
        genre,
        profession,   
        user_goal: userGoal,
        activite_physique : activitePhysique,
        composition_corporelle : compositionCorporelle,
        indicateurs_cardio : indicateursCardio  
      }),
    });

    const data = await response.json();
    console.log("data returned", data);

    if (response.ok) {
      localStorage.setItem("user_id", data.user_id);  // Stocker l'ID utilisateur
      return data;  // Retourner la réponse avec l'ID utilisateur
    } else {
      return { error: data.error || "Échec de l'inscription." };
    }
  } catch (error) {
    console.error("Erreur d'inscription:", error);
    return { error: "Erreur de connexion au serveur" };
  }
};

  


  export const loginUser = async (username: string, password: string) => {
    try {
        const response = await fetch(`${API_URL}login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();
        console.log("data returned 2",data);
        if (response.ok) {
            localStorage.setItem("token", data.access);
            localStorage.setItem("user_id", data.user_id.toString());

            if (data.fitbit_access_token) {
                localStorage.setItem("fitbit_token", data.fitbit_access_token);
                localStorage.setItem("fitbit_refresh_token", data.fitbit_refresh_token);
                localStorage.setItem("fitbit_user_id", data.fitbit_user_id);
            }

            return data;
        } else {
            return { error: data.error || "Échec de la connexion." };
        }
    } catch (error) {
        console.error("Erreur de connexion:", error);
        return { error: "Erreur de connexion au serveur" };
    }
};
