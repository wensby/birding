import React from 'react';
import { CoverNameCard } from './CoverNameCard';
import { useTranslation } from 'react-i18next';
import { useBirdPicture } from './BirdHooks';
import './BirdCover.scss';

export function BirdCover({ bird, commonNames }) {
  const { i18n } = useTranslation();
  const picture = useBirdPicture(bird);
  const language = i18n.languages[0];
  const commonName = commonNames.find(l => l.locale === language);
  return (
    <div className='picture-cover-container'>
      <div className='bird-picture'>
        <img src={picture} alt={bird.id}/>
      </div>
      <CoverNameCard binomial={bird.binomialName} common={commonName.name} />
    </div>
  );
}
