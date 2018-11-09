import React from 'react';
import { Link } from 'react-router-dom';

const CCLink = ({ to, children, className }) => (
  <Link className={`${className}`} to={to}>{children}</Link>
);

export default CCLink;
