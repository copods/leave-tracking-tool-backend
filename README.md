# Leave Tracking Tool Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [User Onboarding](#user-onboarding)
7. [Deployment](#deployment)
8. [Conclusion](#conclusion)

## Introduction

Welcome to the documentation for the Leave Tracking Tool! This tool is designed to facilitate the management of employee leave requests within an organization. It provides a RESTful API built with Django Rest Framework (DRF), utilizes PostgreSQL as the backend database, and implements OAuth2 for authentication and authorization.

## System Overview

The Leave Tracking Tool consists of the following components:

- **Django Backend: Implements the core logic and provides API endpoints for managing leave requests.
- **Django Rest Framework (DRF) Backend**: Implements the core logic and provides API endpoints for managing leave requests and user onboarding.
- **PostgreSQL Database**: Stores data related to users, leave requests, and other application entities.
- **OAuth2 Authentication**: Utilizes OAuth2 for secure authentication and authorization of users accessing the API.

## Database Schema

The database schema for the Leave Tracking Tool includes the following tables:

1. **User**: Stores information about users of the system, including their authentication credentials and profile details.
2. **LeaveRequest**: Tracks leave requests submitted by users, including details such as start date, end date, reason, and status.
3. **LeaveRequestType**: Defines different types/categories of leave requests (e.g., vacation, sick leave, maternity/paternity leave).
4. **Role**: Defines roles or positions within the organization (e.g., Admin, TeamLead, TeamMember, HR).
5. **Department**: Represents organizational departments or units (e.g., HR, Finance, Engg., Design, Marketing, Sales).
The detailed schema definition can be found in the [database_schema.sql](database_schema.sql) file.

## API Endpoints

The API provides the following endpoints for managing leave requests, user onboarding, and additional functionalities:

### Leave Requests

- GET /api/v1/leave/: Retrieves a list of all leave requests.
- POST /api/v1/leave/: Submits a new leave request.
- GET /api/v1/leave/{id}/: Retrieves details of a specific leave request.
- PUT /api/v1/leave/{id}/: Updates details of a specific leave request.
- DELETE /api/v1/leave/{id}/: Cancels a specific leave request.

### User Onboarding

- `POST /api/v1/users/`: Registers a new user and creates their profile.

### Leave Request Types

- GET /api/v1/leave-types/: Retrieves a list of all leave request types.
- POST /api/v1/leave-types/: Creates a new leave request type.
- GET /api/v1/leave-types/{id}/: Retrieves details of a specific leave request type.
- PUT /api/v1/leave-types/{id}/: Updates details of a specific leave request type.
- DELETE /api/v1/leave-types/{id}/: Deletes a specific leave request type.

### Roles

- GET /api/v1/roles/: Retrieves a list of all roles.
- POST /api/v1/roles/: Creates a new role.
- GET /api/v1/roles/{id}/: Retrieves details of a specific role.
- PUT /api/v1/roles/{id}/: Updates details of a specific role.
- DELETE /api/v1/roles/{id}/: Deletes a specific role.

###Departments

- GET /api/v1/departments/: Retrieves a list of all departments.
- POST /api/v1/departments/: Creates a new department.
- GET /api/v1/departments/{id}/: Retrieves details of a specific department.
- PUT /api/v1/departments/{id}/: Updates details of a specific department.
- DELETE /api/v1/departments/{id}/: Deletes a specific department.

The API documentation, including request and response formats, can be found in the [API.md](API.md) file.

## Authentication and Authorization

The Leave Tracking Tool utilizes OAuth2 for authentication and authorization. Users must obtain an access token by authenticating with the OAuth2 provider before accessing protected API endpoints.

The OAuth2 provider generates access tokens that users include in the `Authorization` header of API requests to authenticate and authorize their access.

## User Onboarding

The user onboarding process allows new users to register and create their profile within the system. When a user registers, they provide necessary information such as username, email, and password. Upon successful registration, the user's profile is created in the database.

## Deployment

The Leave Tracking Tool can be deployed to a production environment following these general steps:

1. **Setup PostgreSQL Database**: Configure a PostgreSQL database instance and create the required tables using the provided schema definition.

2. **Deploy Django Rest Framework Backend**: Deploy the Django Rest Framework backend to a web server or platform-as-a-service (PaaS) provider. Configure settings such as database connection details and OAuth2 provider settings.

3. **Configure OAuth2 Provider**: Set up an OAuth2 provider (e.g., Auth0, OAuth2 provider library) to handle user authentication and authorization. Configure the Django backend to use the OAuth2 provider for authentication.

4. **Secure Endpoints**: Secure API endpoints by requiring authentication and authorization tokens in requests to access protected resources.

5. **Testing and Monitoring**: Perform thorough testing of the deployed application to ensure functionality and security. Set up monitoring and logging to track application performance and detect any issues.

## Conclusion

The Leave Tracking Tool provides a robust solution for managing employee leave requests and user onboarding, leveraging Django Rest Framework, PostgreSQL, and OAuth2 for secure and efficient operation. By following the documentation provided, organizations can deploy and utilize this tool to streamline their leave management processes and user registration workflows.
