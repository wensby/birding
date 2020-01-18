import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useReactRouter } from '../../reactRouterHook';
import AuthenticationService from '../AuthenticationService.js';
import RegistrationForm from './CredentialsForm';
import { RegistrationSuccess } from './RegistrationSuccess';
import { FadeIn } from '../../component/FadeIn.js';

export default () => {
  const { match } = useReactRouter();
  const token = match.params.token;
  const [alert, setAlert] = useState(null);
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState(false);
  const [takenUsernames, setTakenUsernames] = useState([]);

  const { t } = useTranslation();
  const authentication = new AuthenticationService();

  useEffect(() => {
    const fetchEmail = async () => {
      const response = await new AuthenticationService().fetchRegistration(token);
      if (response.status === 200) {
        const json = await response.json();
        setEmail(json['email']);
      }
    }
    fetchEmail();
  }, [token]);

  const renderAlert = () => {
    if (alert) {
      return (
        <div className='row'>
          <div className={`col alert alert-${alert.category}`} role='alert'>
            { alert.message }
          </div>
        </div>
      );
    }
  }

  const handleFormSubmit = async credentials => {
    try {
      const response = await authentication.postRegistration(token, credentials);
      if (response.status === 201) {
        setSuccess(true);
      }
      else if (response.status === 409) {
        const json = await response.json();
        if (json['code'] === 3) {
          setTakenUsernames(takenUsernames.concat([credentials[0]]))
          setAlert({
            category: 'danger',
            message: 'Username already taken.',
          });
        }
      }
    }
    catch (err) {
    }
  };

  if (success) {
    return <FadeIn><RegistrationSuccess /></FadeIn>;
  }
  return (
    <div className='container'>
      <div className='row'>
        <div className='col'>
          <h2>{ t('Registration') }</h2>
          <p>
            { t('registration-form-instructions') }
          </p>
        </div>
      </div>
      {renderAlert()}
      <div className='row'>
        <div className='col'>
          <RegistrationForm
            email={email}
            token={token}
            onSubmit={handleFormSubmit}
            takenUsernames={takenUsernames} />
        </div>
      </div>
    </div>
  );
}
