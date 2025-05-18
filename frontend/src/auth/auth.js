export const saveToken = (token) => {
  localStorage.setItem('access_token', token); // Salva o token no localStorage
  //É bom salvar em localStorage para persistir o token entre recarregamentos de página
};

export const getToken = () => {
  return localStorage.getItem('access_token'); // Recupera o token do localStorage
    //Se o token não estiver no localStorage, retorna null
};

export const removeToken = () => {
  localStorage.removeItem('access_token'); // Remove o token do localStorage
    //Isso é útil para fazer logout do usuário
};
