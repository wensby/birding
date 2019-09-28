import React, { useState, useEffect, useContext } from 'react';
import { AuthenticationContext } from '../authentication/AuthenticationContext';
import SightingService from './SightingService.js';

const sightingService = new SightingService();
const SightingContext = React.createContext();

const SightingProvider = props => {
  const { account, token, unauthenticate } = useContext(AuthenticationContext);
  const [sightingsAccount, setSightingsAccount] = useState(null);
  const [sightings, setSightings] = useState([]);

  useEffect(() => {
    if (account != sightingsAccount) {
      setSightings([]);
    }
    setSightingsAccount(account);
  });

  const refreshSightings = async () => {
    const username = account.username;
    const response = await sightingService.fetchSightings(username, token);
    if (response.status == 401) {
      unauthenticate();
    }
    else {
      const content = await response.json();
      if (content.status == 'success') {
        const fetchedSightings = content.result.sightings;
        if (JSON.stringify(sightings) != JSON.stringify(fetchedSightings)) {
          setSightings(fetchedSightings);
        }
      }
    }
  }

  return <SightingContext.Provider value={{
    sightings: sightings,
    refreshSightings: refreshSightings,
  }}>
    {props.children}
  </SightingContext.Provider>;
}

export { SightingProvider, SightingContext };