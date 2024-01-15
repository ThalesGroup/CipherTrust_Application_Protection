// =========================================================
// * Volt React Dashboard
// =========================================================

// * Product Page: https://themesberg.com/product/dashboard/volt-react
// * Copyright 2021 Themesberg (https://www.themesberg.com)
// * Official Repository: https://github.com/themesberg/volt-react-dashboard
// * License: MIT License (https://themesberg.com/licensing)

// * Designed and coded by https://themesberg.com

// =========================================================

// * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. Please contact us to request a removal.

import React from 'react';
import ReactDOM from 'react-dom';
import { HashRouter } from "react-router-dom";
import { useHistory } from "react-router-dom";
import { KindeProvider } from "@kinde-oss/kinde-auth-react";

// core styles
import "./scss/volt.scss";

// vendor styles
import "react-datetime/css/react-datetime.css";

import HomePage from "./pages/HomePage";
import ScrollToTop from "./components/ScrollToTop";

ReactDOM.render(
  <KindeProvider
		clientId={process.env.REACT_APP_AUTH_KEY}
		domain={process.env.REACT_APP_AUTH_URL}
		redirectUri={process.env.REACT_APP_AUTH_REDIRECT_IP}
		logoutUri={process.env.REACT_APP_AUTH_REDIRECT_IP}
    onRedirectCallback={(user, app_state) => {
      window.location = '/#/dashboard'
    }}
	>
    <HashRouter>
      <ScrollToTop />
      <HomePage />
    </HashRouter>
  </KindeProvider>,
  document.getElementById("root")
);
