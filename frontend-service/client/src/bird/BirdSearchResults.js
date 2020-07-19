import React from 'react';
import { RevealableBirdResultCard } from './RevealableBirdResultCard.js';
import { useTranslation } from 'react-i18next';
import './BirdSearchResults.scss';

export const BirdSearchResults = ({ query, birds }) => {
  return (
    <div className='bird-result-container'>
      <BirdSearchResultInfo query={query} />
      {birds.map((item, index) => (
        <RevealableBirdResultCard searchResult={item} key={index} />
      ))}
    </div>
  );
};

const BirdSearchResultInfo = ({ query }) => {
  const { t } = useTranslation();
  return (
    <div className='bird-search-result-info'>
      {t('result-info-label')}: {query}
    </div>
  );
}