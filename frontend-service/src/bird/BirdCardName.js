import React from 'react';
import { useTranslation } from 'react-i18next';

export function BirdCardName({ bird }) {
  const { i18n } = useTranslation();

  const language = i18n.languages[0];

  if (bird.names && bird.names[language]) {
    const localeName = bird.names[language];
    return (
      <>
        <h5 key='1' className="card-title">{localeName}</h5>
        <h6 key='2' className="card-subtitle mb-2 text-muted">
          {bird.binomialName}
        </h6>
      </>
    )
    }
  return <h5 key='1' className="card-title">{bird.binomialName}</h5>;
};
