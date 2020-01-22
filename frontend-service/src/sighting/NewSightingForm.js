import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import SightingService from './SightingService';
import { UserContext } from '../authentication/UserContext';
import { BirdSection } from "./BirdSection";
import { Label } from "./Label";
import { LocationSection } from "./LocationSection";

export function NewSightingForm({ bird, onSuccess }) {
  const { t } = useTranslation();
  const { getAccessToken, account } = useContext(UserContext);
  const [blockedByLocation, setBlockedByLocation] = useState(false);
  const sightingService = new SightingService();
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [location, setLocation] = useState(null);
  const [timeEnabled, setTimeEnabled] = useState(true);

  useEffect(() => {
    const now = new Date();
    setDate(toDateInputValue(now));
    setTime(toTimeInputValue(now));
  }, []);

  useEffect(() => {
    if (timeEnabled) {
      const now = new Date();
      setTime(toTimeInputValue(now));
    }
    else {
      setTime('');
    }
  }, [timeEnabled]);

  const toDateInputValue = date => {
    var local = new Date(date);
    local.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return local.toJSON().slice(0, 10);
  };

  const toTimeInputValue = date => {
    var local = new Date(date);
    local.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return local.toJSON().slice(11, 16);
  };
  const handleFormSubmit = async (event) => {
    event.preventDefault();
    if (!blockedByLocation) {
      const accessToken = await getAccessToken();
      const response = await sightingService.postSighting(accessToken, account.birder.id, bird.binomialName, date, time, location);
      if (response.status === 201) {
        const sightingLocation = response.headers.get('Location');
        const sighting = await sightingService.fetchSightingByLocation(accessToken, sightingLocation);
        onSuccess(sighting);
      }
    }
  };

  return (
    <div className='container sighting-form'>
      <div className='row'>
        <div className='col'>
          <h1>{t('new-sighting-title')}</h1>
          <form onSubmit={handleFormSubmit}>
            <BirdSection bird={bird} />
            <div className='form-group row'>
              <Label htmlFor='dateInput' label='date-label' />
              <div className='col-sm-10'>
                <input type='date' id='dateInput' className='form-control' value={date} onChange={event => setDate(event.target.value)} />
              </div>
            </div>
            <div className='form-group row'>
              <Label htmlFor='timeInput' label='time-label' />
              <div className='input-group col-sm-10' id='timeInput'>
                <div className='input-group-prepend'>
                  <div className='input-group-text'>
                    <input type='checkbox' id='timeCheckboxInput' name='timeCheckboxInput' checked={timeEnabled} onChange={event => setTimeEnabled(event.target.checked)} />
                  </div>
                </div>
                <input type='time' id='timeTimeInput' className='form-control' value={time} disabled={!timeEnabled} onChange={event => setTime(event.target.value)} />
              </div>
            </div>
            <LocationSection onCoordinatesChanged={setLocation} onBlocking={setBlockedByLocation} />
            <input type='hidden' name='birdId' value={bird.id} />
            <button type='submit' className='button' disabled={blockedByLocation}>
              {t('submit-sighting-button')}
            </button>
          </form>
          <Link to='/'>{t('cancel-new-sighting-link')}</Link>
        </div>
      </div>
    </div>
  );
}