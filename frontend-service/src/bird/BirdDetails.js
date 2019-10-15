import React, { useState, useEffect } from 'react';
import BirdService from './BirdService';
import { useTranslation } from 'react-i18next';

export default function BirdDetails(props) {
  const { t } = useTranslation();
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const service = new BirdService();
      const data = await service.getBird(props.match.params.binomialName);
      setData(data.result);
    }
    fetchData();
  }, [props.match.params.binomialName]);

  const renderCoverNameCard = () => {
    return (
      <div className='w-100 d-flex justify-content-center'>
        <div className='shadow bg-white text-center pt-1 mb-0 px-2 rounded-top'>
          <h1 className='text-dark bird-page-name pb-2 mb-0'>
            { t(`bird:${data.binomialName}`) }</h1>
          <p className='font-italic font-weight-light text-muted mb-0 pb-2'>
            { data.binomialName }</p>
        </div>
      </div>
    );
  }

  const renderCover = () => {
    return (
      <div className='picture-cover-container rounded-top overflow-hidden'
        style={{ backgroundImage: `url(${data.coverUrl})` }}>
        <div className='picture-cover'></div>
        {renderCoverNameCard()}
      </div>
    );
  }

  const renderPhotoCredits = () => {
    return (
      <div>
        <p><small>{`Thumbnail Photo by: ${ data.thumbnailCredit }`}</small></p>
      </div>
    );
  }

  if (data) {
    return (
      <div>
        {renderCover()}
        {renderPhotoCredits()}
      </div>
    );
  }
  else {
    return null;
  }
}
