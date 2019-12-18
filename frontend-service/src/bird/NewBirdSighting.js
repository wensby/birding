import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import BirdService from './BirdService';
import SightingService from '../sighting/SightingService';
import { UserContext } from '../authentication/UserContext';
import SightingSuccess from '../sighting/SightingSuccess';
import { usePosition } from '../usePosition';

export default ({ match }) => {
  const binomialName = match.params.binomialName;
  const [addedSighting, setAddedSighting] = useState(null);
  const [bird, setBird] = useState(null);
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [location, setLocation] = useState(null);
  const [locationDisplay, setLocationDisplay] = useState('');
  const [timeEnabled, setTimeEnabled] = useState(true);
  const [locationEnabled, setLocationEnabled] = useState(true);
  const { t } = useTranslation();
  const sightingService = new SightingService();
  const { getAccessToken, account } = useContext(UserContext);
  const { latitude, longitude, error } = usePosition();
  const { i18n } = useTranslation();
  const language = i18n.languages[0];

  useEffect(() => {
    const fetchData = async () => {
      const data = await new BirdService().getBird(binomialName);
      setBird(data);
    }
    fetchData();
    const now = new Date();
    setDate(toDateInputValue(now));
    setTime(toTimeInputValue(now));
  }, [binomialName]);

  useEffect(() => {
    if (timeEnabled) {
      const now = new Date();
      setTime(toTimeInputValue(now));
    }
    else {
      setTime('');
    }
  }, [timeEnabled]);

  useEffect(() => {
    const fetchLocationDisplay = async (latitude, longitude) => {
      const headers = new Headers({
        'User-Agent': 'Aveslog.com'
      });
      const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=21&addressdetails=1&accept-language=${language}`, {
        headers: headers,
      });
      if (response.status == 200) {
        const json = await response.json();
        setLocation([latitude, longitude]);
        setLocationDisplay(json.display_name);
      }
    }
    if (locationEnabled && latitude && longitude) {
      fetchLocationDisplay(latitude, longitude);
    }
    else {
      setLocation(null);
    }
  }, [locationEnabled, latitude, longitude, language])

  const handleFormSubmit = async event => {
    event.preventDefault();
    const accessToken = await getAccessToken();
    const response = await sightingService.postSighting(
      accessToken, account.birder.id, bird.binomialName, date, time, location,
    );
    if (response.status === 201) {
      const sightingLocation = response.headers.get('Location');
      const sighting = await sightingService.fetchSightingByLocation(accessToken, sightingLocation);
      setAddedSighting(sighting);
    }
  }

  const toDateInputValue = date => {
    var local = new Date(date);
    local.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return local.toJSON().slice(0, 10);
  }

  const toTimeInputValue = date => {
    var local = new Date(date);
    local.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return local.toJSON().slice(11, 16);
  }

  if (!bird) {
    return null;
  }

  if (addedSighting) {
    return <SightingSuccess sighting={addedSighting}/>;
  }

  return (
    <div className='container'>
      <div className='row'>
        <div className='col'>
          <h1>{t('new-sighting-title')}</h1>
          <form onSubmit={handleFormSubmit}>
            <BirdSection bird={bird} />
            <div className='form-group row'>
              <Label htmlFor='dateInput' label='date-label' />
              <div className='col-sm-10'>
                <input type='date' id='dateInput' className='form-control'
                  value={date}
                  onChange={event => setDate(event.target.value)} />
              </div>
            </div>
            <div className='form-group row'>
              <Label htmlFor='timeInput' label='time-label' />
              <div className='input-group col-sm-10' id='timeInput'>
                <div className='input-group-prepend'>
                  <div className='input-group-text'>
                    <input type='checkbox' id='timeCheckboxInput'
                      name='timeCheckboxInput' checked={timeEnabled}
                      onChange={event => setTimeEnabled(event.target.checked)} />
                  </div>
                </div>
                <input type='time' id='timeTimeInput' className='form-control'
                  value={time} disabled={!timeEnabled}
                  onChange={event => setTime(event.target.value)} />
              </div>
            </div>
            <div className='form-group row'>
              <Label htmlFor='locationInput' label='location-label' />
              <div className='input-group col-sm-10' id='locationInput'>
                <div className='input-group-prepend'>
                  <div className='input-group-text'>
                    <input type='checkbox' id='locationCheckboxInput'
                      name='locationCheckboxInput' checked={locationEnabled}
                      onChange={event => setLocationEnabled(event.target.checked)} />
                  </div>
                </div>
                <input type='text' id='locationTextInput' className='form-control'
                  value={!location ? '' : locationDisplay} disabled />
              </div>
            </div>
            <input type='hidden' name='birdId' value={bird.id} />
            <button type='submit' className='button'>
              {t('submit-sighting-button')}
            </button>
          </form>
          <Link to='/'>{t('cancel-new-sighting-link')}</Link>
        </div>
      </div>
    </div>
  );
}

const BirdSection = ({ bird }) => {
  const { i18n } = useTranslation();
  const language = i18n.languages[0];
  const name = bird.names && bird.names[language] ? bird.names[language] : bird.binomialName;

  return (
    <div className='form-group row'>
      <Label htmlFor='birdInput' label='bird-label' />
      <div className='col-sm-10'>
        <input id='birdInput' type='text' readOnly
          className='col-sm-10 form-control-plaintext'
          value={name} />
      </div>
    </div>
  );
};

const Label = ({ htmlFor, label }) => {
  const { t } = useTranslation();
  const className = 'col-sm-2 col-form-label';
  return <label htmlFor={htmlFor} className={className}>{t(label)}</label>;
};
