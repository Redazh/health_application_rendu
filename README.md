# Health Application Setup Guide  

## Installation Guide  

### 1. Install Dependencies  

#### **Frontend - Install Ionic CLI**  
Navigate to the frontend directory and install the Ionic CLI:  

```sh
cd frontend
npm install -g @ionic/cli
```

#### **Backend - Install Required Python Packages**  
Navigate to the backend directory and install the necessary dependencies:  

```sh
cd ..
cd backend
pip install djangorestframework-simplejwt
pip install dj-rest-auth
pip install django-allauth
pip install psycopg2-binary
pip install cryptography
pip install pandas
pip install scikit-learn
```

---

### 2. Connect PostgreSQL Database  

#### **Step 1: Install PostgreSQL and pgAdmin**  
Download and install:  

- **PostgreSQL 17**  
- **pgAdmin**  

#### **Step 2: Create a Database in PostgreSQL**  
1. Open **pgAdmin**.  
2. Create a new database with the following configuration:  

   ```yaml
   NAME: database
   USER: myuser
   PASSWORD: mypassword
   HOST: localhost
   PORT: 5432
   ```

#### **Step 3: Create PostgreSQL User (`myuser`)**  
1. Open **pgAdmin**.  
2. Go to **Query Tool**.  
3. Run the following SQL commands:  

   ```sql
   CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
   CREATE DATABASE database OWNER myuser;
   ALTER ROLE myuser SET client_encoding TO 'utf8';
   ALTER ROLE myuser SET default_transaction_isolation TO 'read committed';
   ALTER ROLE myuser SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE database TO myuser;
   GRANT ALL ON SCHEMA public TO myuser;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
   ```

---

### 3. Set Up Google Authentication  

#### **Step 1: Create a Superuser for the Django Admin Panel**  
Run the following command and provide a username, email, and password when prompted:  

```sh
python manage.py createsuperuser
```

#### **Step 2: Start the Backend Server**  
Navigate to the backend folder and execute:  

```sh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

The backend will now run at **http://127.0.0.1:8000/**.  

1. Open **http://127.0.0.1:8000/admin** in a browser.  
2. Log in using the superuser credentials.  
3. Go to **Sites**, delete `example.com`, and add:  

   ```
   Domain Name: http://127.0.0.1:8000
   Display Name: http://127.0.0.1:8000
   ```

4. In the Admin Panel, go to **Social Applications** and click **Add**.  
   - **Provider**: Google  
   - **Name**: google_auth_health_app  
   - **Client ID**: `278704582350-en3kaen8kes3m412klp3l1s341feeth7.apps.googleusercontent.com`  
   - **Secret Key**: `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`  

5. Save the configuration.

---

## Running the Project  

### **Step 1: Start the Backend Server**  
Navigate to the backend folder and execute:  

```sh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### **Step 2: Start the Frontend Application**  
Open a new terminal, navigate to the frontend folder, and run:  

```sh
ionic serve
```

### **Step 3: Access the Application**  
Open **http://localhost:8100** in a web browser to access the frontend.
