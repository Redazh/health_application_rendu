import { IonApp, setupIonicReact } from "@ionic/react";
import { IonReactRouter } from "@ionic/react-router";
import { BrowserRouter as Router, Route, Switch, Redirect } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import CompleteProfile from "./pages/CompleteProfile";
import Friends from "./pages/Friends";
import Groups from "./pages/Groups"; 
import GroupPage from "./pages/GroupPage";
import Class from "./pages/Class";

/* Core CSS required for Ionic components to work properly */
import "@ionic/react/css/core.css";

/* Basic CSS for apps built with Ionic */
import "@ionic/react/css/normalize.css";
import "@ionic/react/css/structure.css";
import "@ionic/react/css/typography.css";

/* Optional CSS utils that can be commented out */
import "@ionic/react/css/padding.css";
import "@ionic/react/css/float-elements.css";
import "@ionic/react/css/text-alignment.css";
import "@ionic/react/css/text-transformation.css";
import "@ionic/react/css/flex-utils.css";
import "@ionic/react/css/display.css";

/* Dark Mode */
import "@ionic/react/css/palettes/dark.system.css";

/* Theme variables */
import "./theme/variables.css";
import Callback from "./pages/Callback";
import Workout from "./pages/Workout";
import Nutrition from "./pages/Nutrition";
setupIonicReact();

const App: React.FC = () => {
  return (
    <GoogleOAuthProvider clientId="278704582350-en3kaen8kes3m412klp3l1s341feeth7.apps.googleusercontent.com">
      <Router>
        <Switch> {/* Replace Routes with Switch */}
          <Route  path="/home" component={Home} />
          <Route path="/login" component={Login} />
          <Route path="/register" component={Register} />
          <Route path="/dashboard" component={Dashboard} />
          <Route path="/complete-profile" component={CompleteProfile} />
          <Route path="/friends" component={Friends} />
          <Route path="/groups" component={Groups} />  
          <Route path="/group/:id" component={GroupPage} />  
          <Route path="/callback2" component={Callback} />
          <Route exact path="/class" component={Class} />
          <Route exact path="/Workout" component={Workout} />
          <Route exact path="/Nutrition" component={Nutrition} />
          {/*  Redirect unknown routes to /login */}
          <Redirect to="/login" />
        </Switch>
      </Router>
    </GoogleOAuthProvider>
  );
};

export default App;