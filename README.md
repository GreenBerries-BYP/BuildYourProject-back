
<h1 align="center">🚀 Build Your Project</h1>
<p align="center">
  Uma aplicação fullstack em <strong>Django</strong> + <strong>React</strong> para facilitar o desenvolvimento e gestão de projetos.
</p>

<p align="center">
  <img src="BYP_logo_slogan.png" alt="Logo do Build Your Project" width="500" />
</p>


<p align="center">
  <strong>🛠️ Projeto em desenvolvimento ativo - open source</strong>
</p>

---



**Conteúdo**

- [Instalar e rodar o projeto](#instalar-e-rodar-o-projeto)
  - [Dependências globais](#dependências-globais)
  - [Dependências locais](#dependências-locais)
  - [Rodar o projeto](#rodar-o-projeto)
- [Equipe](#-equipe)

## Instalar e rodar o projeto

### Dependências globais

- Python 3.10+
- Node.js 18+

### Dependências locais

Com o repositório clonado:

```bash
# Backend
cd backend
poetry install
poetry env activate 
pip install dj-database-url psycopg2-binary
pip install google-auth
pip install python-dotenv
pip install djangorestframework
pip install django-cors-headers

# Frontend
cd ../frontend
npm install
```

### Rodar o projeto
```bash
cd backend
python manage.py runserver
```
Em outro terminal, rodar o frontend
```bash
cd frontend
npm run dev
```
## 👥 Equipe

<div align="center">

| [João](https://github.com/jpfelixx) | [Jossana](https://github.com/JojoMarques) | [Leticia](https://github.com/lelerudeli) |
|---|---|---|
| <img src="https://github.com/jpfelixx.png" width="100"/> | <img src="https://github.com/JojoMarques.png" width="100"/> | <img src="https://github.com/lelerudeli.png" width="100"/> |

| [Marisa](https://github.com/maris2606) | [Millena](https://github.com/Mihcup) | [Rodrigo](https://github.com/RodrigoBettio) |
|---|---|---|
| <img src="https://github.com/maris2606.png" width="100"/> | <img src="https://github.com/Mihcup.png" width="100"/> | <img src="https://github.com/RodrigoBettio.png" width="100"/> |

</div>


![Alt](https://repobeats.axiom.co/api/embed/e6dded7619f898ccb363c37cbd862c9a48978b95.svg "Repobeats analytics image")
