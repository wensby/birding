import React from 'react';
import BirdResultCard from './BirdResultCard';
import { useTranslation } from 'react-i18next';
import './style.scss';

export function BirdSearchResults({ query, birds }) {
  const { t } = useTranslation();

  return (
    <div className='bird-result-container text-break'>
      <div className='info'>{t('result-info-label')}: {query}</div>
      {birds.map((item, index) => <BirdSearchResultItem
        item={item}
        key={index}
      />)}
    </div>
  );
};

function BirdSearchResultItem({ item, ...props }) {
  return (
    <React.Fragment {...props}>
      <BirdResultCard searchResult={item} />
    </React.Fragment>
  );
}