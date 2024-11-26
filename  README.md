# FastAPI Application

This is a FastAPI application that you can run using Docker. To get the application up and running, follow these steps: 

1. Clone the project repository to your local machine.

2. Navigate to the `app` directory: `cd app`

3. Create a `.env` file with the following variables:
   ```plaintext
   DB_HOST=postgres
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=postgres
   CAT_API_KEY=live_AKQeZauXu50dAj7fOlMBvoafzTu5tMy3eypN5dBRzB6aoENtgY2W4sp2uYzwTiEL
   
4. Build and run the application using Docker Compose: `docker-compose up --build`
5. Once the application is running, open your web browser and go to the following URL to access the Swagger documentation: [http://0.0.0.0:1715/api/schema/swagger-ui/](http://0.0.0.0:1715/docs)


