import React from 'react';
import BirdCardPicture from './BirdCardPicture';
import BirdLink from './BirdLink';

export default function BirdCard({ bird, key, children }) {
  return (
    <div key={key} className="card">
      <div className="card-horizontal">
        <div className="img-square-wrapper">
          <BirdLink bird={bird} >
            <BirdCardPicture bird={bird} />
          </BirdLink>
        </div>
        {children}
      </div>
    </div>
  );
};
