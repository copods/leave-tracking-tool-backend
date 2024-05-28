# Leave Tracking Tool Documentation

Welcome to Copods backend, where we transform ideas into robust web applications! 🚀

Dive into the heart of our Django project, powered by a PostgreSQL database, and embark on a journey of coding excellence. Here's your ticket to get started:

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python (3.x recommended)

- PostgreSQL (PgAdmin 4 GUI)

## Setting Up Locally

1. Clone the repository to your local machine:

```bash

git clone https://github.com/copods/leave-tracking-tool-backend.git

```

2. Navigate into the project directory:

```bash

cd leave-tracking-tool-backend/

```

3. Create a new virtual environment:

```bash

python3 -m venv .venv

```

4. Activate the virtual environment:

- On Windows:

```bash

.venv\Scripts\activate

```

- On macOS and Linux:

```bash

source .venv/bin/activate

```

5. Install the necessary Django packages:

```bash

pip install -r requirements.txt

```

### Installing PostgreSQL with pgAdmin (MacOS/Windows)

1.  **Download PostgreSQL Installer:**

- Visit the [official PostgreSQL download page](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) for MacOS/Windows.

- Choose the PostgreSQL version 16.3

- Click on the download link to download the PostgreSQL installer.

2.  **Run the Installer:**

- Once the installer is downloaded, double-click on it to run it.

- Follow the installation wizard's instructions:

- Choose the installation directory.

- Select the components to install. Make sure to select pgAdmin as one of the components to install.

- Choose a password for the `postgres` user when prompted.

3.  **Install pgAdmin:**

- During the PostgreSQL installation, make sure to select pgAdmin for installation.

4.  **Complete the Installation:**

- Continue following the installation wizard's instructions until the installation process is complete.

5.  **Start pgAdmin:**

- After the installation is finished, you can start pgAdmin by searching for it in the Start menu or launching it from the installed directory.

  - **Launch pgAdmin:** Open pgAdmin and log in with your credentials.
  - **Connect to PostgreSQL Server:** In pgAdmin, navigate to the "Servers" section in the left sidebar. Open "Servers" and then Right-click on "PostgreSQL" and choose "Create" > "Database...". Enter the necessary connection details:

    ### CREATE SERVER INFORMATION

    - **Name** Enter `Copods-LTT`.
    - **Connection Hostname/Address:** Use `localhost` or `127.0.0.1`.
    - **Username:** Enter `postgres`.
    - **Password:** Provide the password you set during PostgreSQL installation.
    - **Port:** Default PostgreSQL port is `5432`.

    ### CREATE DATABASE INFORMATION

    - **Databse**: Enter `Leave-Tracking-Tool`

### Setting Up PostgreSQL Database in pgAdmin

Now you have PostgreSQL installed with pgAdmin and a database set up ready for use with your Django project. Make sure to update your Django project's settings to use the newly created PostgreSQL database.

1. Create a `.env` file in the project directory with the following format:

```plaintext

DB_NAME=Leave-Tracking-Tool

DB_USER=postgres

DB_PASSWORD=admin

DB_HOST=127.0.0.1

DB_PORT=5432

SECRET_KEY = "ABCD-Replacehere"

```

## Migrate the models into the database:

```bash

python manage.py makemigrations

python manage.py migrate

```

## to create empty migration

```bash
python manage.py makemigrations your_app_name --empty --name add_initial_data
```

## Creating a Superuser

1. Navigate to your Django project directory if you're not already there.

2. Run the following command to create a superuser:

```bash

python manage.py createsuperuser

```

3. Follow the prompts to enter a username, email, and password for the superuser account.

## Running the Development Server

1. Start the Django development server:

```bash

python manage.py runserver

```

2. Open your web browser and visit `http://127.0.0.1:8000/` to view your Django project.

3. To access the Django admin interface, go to `http://127.0.0.1:8000/admin/` and log in using the superuser credentials you created.

## Resources

- [Django Documentation](https://docs.djangoproject.com/en/stable/)

- [DRF - DjangoRestFrameork](https://www.django-rest-framework.org/)

## Naming conventions followed

- [App Name] : snake_case.
- [App File] : snake_case.
- [Class Name] : PascalCase.
- [Function Name] : snake_case.
- [Global constants] : CAPITAL_CASE.
