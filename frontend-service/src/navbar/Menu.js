import React from 'react';
import { Link } from 'react-router-dom';

export function Menu({ onClick, items }) {

  const renderItem = (item, index) => {
    return (
      <div className="nav-item" key={index} onClick={onClick}>
        <Link className='nav-link' to={item.link} onClick={item.action}>{item.label}</Link>
      </div>
    );
  };

  return (
    <div className='navbar-nav mr-auto' id='collapsableMenuList'>
      {items.map(renderItem)}
    </div>
  );
}
