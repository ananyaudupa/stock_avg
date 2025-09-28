# Use a lightweight Nginx image
FROM nginx:alpine

# Copy your static site (HTML/CSS/JS) to nginx's default folder
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Nginx runs automatically
