import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { SearchBarContext } from './SearchBar';
import './SearchButton.scss';

export const SearchButton = () => {
  const { dirty, advanced } = useContext(SearchBarContext);
  const { t } = useTranslation();

  const classNames = ['search-button'];
  
  if (dirty || advanced) {
    classNames.push('expanded');
  }
  
  const className = classNames.join(' ');
  
  return <button className={className} type='submit'>{t('Search')}</button>;
};
