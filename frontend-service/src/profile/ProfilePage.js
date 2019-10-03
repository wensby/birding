import React, { useState, useContext, useEffect } from 'react';
import SightingService from '../sighting/SightingService';
import { AuthenticationContext } from '../authentication/AuthenticationContext';
import SightingItem from '../sighting/SightingItem';

export default ({ username }) => {
  const [sightings, setSightings] = useState([]);
  const { token } = useContext(AuthenticationContext);
  const sightingService = new SightingService();

  const fetchSightings = async () => {
    const response = await sightingService.fetchSightings(username, token);
    if (response.status == 401) {
      
    }
    else {
      const content = await response.json();
      if (content.status == 'success') {
        setSightings(content.result.sightings);
      }
    }
  }

  useEffect(() => {
    fetchSightings();
  }, [username]);

  const renderSightings = () => {
    return sightings.map(sighting => <SightingItem sighting={sighting} />);
  }

  return (
    <>
      <h1>{username}</h1>
      {renderSightings()}
    </>
  );
};
