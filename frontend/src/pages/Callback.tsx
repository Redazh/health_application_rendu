import { useEffect } from "react";
import { useHistory } from "react-router-dom";

const Callback: React.FC = () => {
  const history = useHistory();

  useEffect(() => {
    const fetchToken = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get("code");
      const user_id = localStorage.getItem("user_id");
      if (localStorage.getItem("fitbit_code_used") === code) {
        console.log("Authorization code already used, skipping duplicate request.");
        return;
      }
      if (code && user_id) {
        localStorage.setItem("fitbit_code_used", code);
        const response = await fetch("http://127.0.0.1:8000/api/auth/fitbit/", {
          method: "POST",
          headers: { "Content-Type": "application/json" }, // No Authorization header
          body: JSON.stringify({ code, user_id }),
        });

        const data = await response.json();
        console.log("Fitbit Auth Response:", data);

        if (data.access_token) {
          localStorage.setItem("fitbit_token", data.access_token);
          localStorage.setItem("fitbit_refresh_token", data.refresh_token); // Store refresh token
          alert("Connexion Fitbit réussie !");
          history.push("/dahsboard");
        } else {
          alert("Erreur de connexion avec Fitbit.");
        }
      }
    };

    fetchToken();
  }, [history]);

  return <p>Connexion en cours...</p>;
};

export default Callback;
