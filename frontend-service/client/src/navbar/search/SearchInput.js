import React, { useContext } from 'react';
import { SearchContext } from '../../search/SearchContext';
import { useTranslation } from 'react-i18next';
import './SearchInput.scss';

export const SearchInput = React.forwardRef((props, ref) => {
  const { query, setQuery } = useContext(SearchContext);
  const { t } = useTranslation();

  const label = t('Search bird');

  const handleChange = event => {
    setQuery(event.target.value);
  };

  return (
    <div className='search-input'>
      <input ref={ref} placeholder={label}
        aria-label={label} onChange={handleChange} value={query} />
      {props.children}
    </div>
  );
});
