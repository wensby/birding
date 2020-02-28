import React, { useState } from 'react';
import placeholder from './placeholder-bird.jpg';
import './BirdThumbnailImage.scss';

export const BirdThumbnailImage = ({ bird, ...other }) => {
  const [src, setSrc] = useState(((bird || {}).thumbnail || {}).url || placeholder);
  return <img
    className='bird-thumbnail'
    onError={() => setSrc(placeholder)}
    src={src}
    alt="Card"
    {...other}
  />;
};