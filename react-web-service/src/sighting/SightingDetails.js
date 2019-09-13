import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import birdRepository from '../bird/BirdRepository';
import SightingService from './SightingService';
import { AuthenticationContext } from '../authentication/AuthenticationContext';

export default function SightingDetails(props) {
  const sightingId = props.match.params.sightingId;
  const [sighting, setSighting] = useState(null);
  const [bird, setBird] = useState(null);
  const { token } = useContext(AuthenticationContext);
  const { t } = useTranslation();
  const sightingService = new SightingService();

  const resolveData = async () => {
    const response = await sightingService.fetchSighting(token, sightingId);
    if (response.status == 'success') {
      const sighting = response.result;
      const bird = await birdRepository.getBird(sighting.birdId);
      setSighting(sighting);
      setBird(bird);
    }
  }

  useEffect(() => {
    resolveData();
  }, []);

  if (!sighting || !bird) {
    return null;
  }
  return (
    <div className='container'>
      <h1>{ t(`bird:${bird.binomialName}`) }</h1>
      <form onSubmit={() => {}}>
        <button type='submit' value='Delete' className='btn btn-danger'>
          {t('delete-sighting-button')}
        </button>
      </form>
    </div>
  );
}
