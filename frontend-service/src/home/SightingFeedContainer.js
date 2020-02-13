import React, { useContext, useState, useEffect } from 'react';
import { SightingFeed } from './SightingFeed';
import { UserContext } from '../authentication/UserContext';
import SightingService from '../sighting/SightingService';

export function SightingFeedContainer() {
  const { accessToken } = useContext(UserContext);
  const [sightings, setSightings] = useState([]);

  useEffect(() => {
    const fetchSightings = async () => {
      const response = await new SightingService().getSightingFeedSightings(accessToken);
      if (response.status === 200) {
        const json = await response.json();
        setSightings(json.items);
      }
    }
    fetchSightings();
  }, [accessToken]);

  return <SightingFeed sightings={sightings} />;
}
