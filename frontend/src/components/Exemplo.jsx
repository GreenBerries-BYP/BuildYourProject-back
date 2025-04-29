import React, { useEffect, useState } from 'react';
import api from '../api/api';

const Exemplo = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.get('/hello/')
      .then(res => setMessage(res.data.message))
      .catch(err => console.error(err));
  }, []);

  return <h1>{message || 'Carregando...'}</h1>;
};

export default Exemplo;
