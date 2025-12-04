# academia_manager

Um gestor para controle de cadastros e pagamentos de alunos da academia
**CT AÇÃO** (professora Alana Sampaio --- Jacobina/BA).\
Permite gerenciar alunos, matrículas, pagamentos e histórico de forma
simples via interface web.

## ✨ Funcionalidades principais

-   Cadastro de alunos (nome, dados pessoais, contato, etc.)\
-   Registro de matrículas e planos de pagamento\
-   Controle de mensalidades e pagamentos realizadas / pendentes\
-   Visualização de lista de alunos ativos / inativos\
-   Interface web amigável (frontend + backend) para gerenciamento

## 🧰 Tecnologias utilizadas

-   Python (Django) --- backend\
-   HTML / CSS / JavaScript --- frontend\
-   Templates Django --- renderização de páginas\
-   (Outras dependências presentes no `requirements.txt`)

## 🚀 Como rodar localmente

1.  Clone o repositório:

    ``` bash
    git clone https://github.com/alexandre-fo-filho/academia_manager.git
    ```

2.  Acesse a pasta do projeto:

    ``` bash
    cd academia_manager
    ```

3.  Crie um ambiente virtual:

    ``` bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS  
    venv\Scripts\activate   # Windows
    ```

4.  Instale dependências:

    ``` bash
    pip install -r requirements.txt
    ```

5.  Aplique migrações:

    ``` bash
    python manage.py migrate
    ```

6.  Inicie o servidor:

    ``` bash
    python manage.py runserver
    ```

7.  Acesse: `http://127.0.0.1:8000/`

## 📂 Estrutura do projeto

-   `academia_manager/` --- app Django principal\
-   `alunos/` --- módulo de alunos\
-   `static/` --- arquivos estáticos\
-   `templates/` --- templates HTML\
-   `manage.py` --- utilitário Django\
-   `requirements.txt` --- dependências

## 📄 Licença

Adicione aqui a licença apropriada (ex.: MIT, GPL etc.).

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra issues ou pull requests para
melhorias.
