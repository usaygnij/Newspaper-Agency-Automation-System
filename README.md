# Software Installation and Execution Guide

## Prerequisites
Before running the software, make sure you have the following prerequisites installed:

- [Django](https://www.djangoproject.com/): `pip install django`
- [Django REST framework](https://www.django-rest-framework.org/): `pip install djangorestframework`
- [Django MultiSelectField](https://pypi.org/project/django-multiselectfield/): `pip install django-multiselectfield`
- [FPDF](https://pypi.org/project/fpdf/): `pip install fpdf`

## Execution
Follow these steps to execute the software:

1. **Make Migrations**: Execute the following command to create migrations for the specified folder:

    ```bash
    python manage.py makemigrations folder_name
    ```

2. **Create Superuser**: Create a superuser account by running the following command and following the prompts:

    ```bash
    python manage.py createsuperuser
    ```

3. **Apply Migrations**: Apply the migrations to the database using the following command:

    ```bash
    python manage.py migrate
    ```

4. **Run Server**: Finally, run the Django development server with the following command:

    ```bash
    python manage.py runserver
    ```

Once the server is running, you can access the software at `http://localhost:8000/`.

## Additional Notes
- Make sure to replace `folder_name` in the `makemigrations` command with the actual name of your Django app folder.
- Ensure that your virtual environment is activated before running the `pip` and `python` commands.
