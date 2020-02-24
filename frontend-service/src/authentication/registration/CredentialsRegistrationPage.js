import React, { useState } from 'react';
import { useReactRouter } from '../../reactRouterHook';
import { RegistrationSuccess } from './RegistrationSuccess';
import { FadeIn } from '../../component/FadeIn.js';
import { useHistory } from "react-router-dom";
import { useRegistrationRequest } from '../AuthenticationHooks.js';
import { CredentialsRegistration } from './CredentialsRegistration';
import { LoadingOverlay } from '../../loading/LoadingOverlay.js';

export const CredentialsRegistrationPage = () => {
  const { match } = useReactRouter();
  const [success, setSuccess] = useState(false);
  const { token } = match.params;
  const { registrationRequest, error } = useRegistrationRequest(token);
  const history = useHistory();

  const handleSuccess = () => {
    setSuccess(true);
  };

  if (error === 404) {
    history.push('/authentication/login');
  }
  if (success) {
    return <FadeIn><RegistrationSuccess /></FadeIn>;
  }
  else if (!registrationRequest) {
    return <LoadingOverlay />;
  }
  return <CredentialsRegistration
    registrationRequest={registrationRequest}
    onSuccess={handleSuccess} />;
};

