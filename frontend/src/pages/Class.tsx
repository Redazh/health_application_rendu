import React from "react";
import { useLocation, useHistory } from "react-router-dom";
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonButton,
} from "@ionic/react";
import CircularGauge from "./CircularGauge"; // Your gauge component
import "./Class.css";

const Class: React.FC = () => {
  const location = useLocation<{
    assignedCluster: number;
    pcaValues: Record<string, number>;
  }>();
  const history = useHistory();

  // Extract cluster and PCA values using descriptive keys
  const assignedCluster = location.state?.assignedCluster ?? "Non défini";
  const pcaValues = location.state?.pcaValues ?? {
    "Activity vs. Sedentary Lifestyle (PC1)": 0,
    "Body Metrics & Energy Expenditure (PC2)": 0,
    "Cardiovascular & Fitness Indicator (PC3)": 0,
  };

  // Extract values using the descriptive keys
  const pc1Value = pcaValues["Activity vs. Sedentary Lifestyle (PC1)"];
  const pc2Value = pcaValues["Body Metrics & Energy Expenditure (PC2)"];
  const pc3Value = pcaValues["Cardiovascular & Fitness Indicator (PC3)"];

  // Cluster interpretations for each PCA component
  const pc1_clusters = [
    { value: -4.03, label: "🏃‍♂️ Very Active" },
    { value: -1.68, label: "🚶 Moderately Active" },
    { value: +1.78, label: "🛋️ Very Low Activity" },
    { value: -0.77, label: "📉 Less Active" },
  ];

  const pc2_clusters = [
    { value: +2.52, label: "🍏 Lean, Low Calorie Burn" },
    { value: -2.00, label: "⚖️ High Calorie Burn" },
    { value: -1.40, label: "🥩 Heavier, High Calorie Burn" },
    { value: +1.79, label: "📊 Moderate BMI" },
    { value: +1.15, label: "🔥 High BMI, High Calories" },
  ];

  const pc3_clusters = [
    { value: +1.44, label: "❤️ High PC3 - Low Fitness" },
    { value: +0.42, label: "🏋️‍♂️ Medium PC3 - Mixed" },
    { value: +2.09, label: "🔥 Low PC3 - High Fitness" },
    { value: +0.55, label: "⚡ Mixed PC3" },
    { value: -1.70, label: "🏆 Very Low PC3 - Best Fitness" },
  ];

  // Function to find the closest cluster label
  const getClosestLabel = (
    value: number,
    clusters: { value: number; label: string }[]
  ) => {
    return clusters.reduce((prev, curr) =>
      Math.abs(curr.value - value) < Math.abs(prev.value - value) ? curr : prev
    ).label;
  };

  const pc1_label = getClosestLabel(pc1Value, pc1_clusters);
  const pc2_label = getClosestLabel(pc2Value, pc2_clusters);
  const pc3_label = getClosestLabel(pc3Value, pc3_clusters);

  const getClusterInterpretation = (cluster: number) => {
    switch (cluster) {
      case 1:
        return "🏃‍♂️ Cluster 1: Très actif - Beaucoup de pas, distances élevées, peu de temps sédentaire.";
      case 2:
        return "🚶 Cluster 2: Activité modérée - Bonne balance entre activité et repos.";
      case 3:
        return "🛋️ Cluster 3: Peu actif - Mode de vie plutôt sédentaire, peu de distance parcourue.";
      case 4:
        return "📉 Cluster 4: Sédentaire - Très peu d’activité physique, besoin d’amélioration.";
      case 5:
        return "⚖️ Cluster 5: Mixte - Un peu d’activité, mais pas encore optimal.";
      default:
        return "❓ Cluster inconnu.";
    }
  };

  return (
    <IonPage>
      <IonHeader className="elegant-header">
        <IonToolbar>
          <IonTitle>Votre Classification</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="elegant-content">
        <div className="elegant-container">
          <IonCard className="elegant-card">
            <IonCardHeader>
              <IonCardTitle> Votre Cluster</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <h2>Cluster Assigné : {assignedCluster}</h2>
              <p>{getClusterInterpretation(assignedCluster)}</p>
            </IonCardContent>
          </IonCard>
          <IonCard className="elegant-card">
            <IonCardHeader>
              <IonCardTitle>Résumé des PCA</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <div className="gauge-row-horizontal">
                <div className="gauge-item">
                  <CircularGauge value={pc1Value} text={`${pc1Value}`} />
                  <p className="gauge-label">Activity vs. Sedentary (PC1)</p>
                </div>
                <div className="gauge-item">
                  <CircularGauge value={pc2Value} text={`${pc2Value}`} />
                  <p className="gauge-label">Body Metrics & Energy (PC2)</p>
                </div>
                <div className="gauge-item">
                  <CircularGauge value={pc3Value} text={`${pc3Value}`} />
                  <p className="gauge-label">Cardio & Fitness (PC3)</p>
                </div>
              </div>
            </IonCardContent>
          </IonCard>
          <IonCard className="elegant-card">
            <IonCardHeader>
              <IonCardTitle>Interprétation Personnalisée</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <p><b>PC1 :</b> {pc1_label}</p>
              <p><b>PC2 :</b> {pc2_label}</p>
              <p><b>PC3 :</b> {pc3_label}</p>
            </IonCardContent>
          </IonCard>
          <div className="button-container">
            <IonButton className="elegant-button" expand="full" onClick={() => history.push("/dashboard")}>
              🔙 Retour au Dashboard
            </IonButton>
          </div>
        </div>
      </IonContent>
    </IonPage>
  );
};

export default Class;