# Quantum Hub SMS - Deployment Guide for Ubuntu Server

This guide will help you deploy the Quantum Hub SMS application on an Ubuntu Server using Docker.

## Prerequisites

- Ubuntu Server 20.04 LTS or newer
- SSH access to your server
- Domain name (optional, but recommended for production)

## Server Setup Steps

### 1. Update Server and Install Required Packages

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y docker.io docker-compose git
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Log out and log back in to apply the docker group membership.

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/quantum-hub-sms.git
cd quantum-hub-sms
```

Or upload your code using SFTP/SCP.

### 3. Configure Environment Variables

```bash
cp .env.example .env
nano .env  # or vim .env
```

Update the environment variables with secure values:
- Change SECRET_KEY to a secure random string
- Update DATABASE_URL if needed
- Add your SMS service API credentials
- Change the default admin password

### 4. Configure Nginx for Your Domain (Optional)

If you're using a domain name, update the Nginx configuration:

```bash
nano nginx/conf.d/app.conf
```

Change the `server_name` directive to your domain:

```
server_name yourdomain.com www.yourdomain.com;
```

### 5. Start the Application

```bash
docker-compose up -d
```

This will start all services in detached mode.

### 6. Set Up SSL with Let's Encrypt (Recommended for Production)

Install Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Follow the prompts to set up SSL.

### 7. Monitor the Application

Check the application logs:

```bash
docker-compose logs -f
```

### 8. Backup Strategy

Set up regular database backups:

```bash
# Create a backup directory
mkdir -p ~/backups

# Add a cron job to backup the database daily
(crontab -l 2>/dev/null; echo "0 2 * * * docker exec quantum-hub-sms_db_1 pg_dump -U postgres smsapp > ~/backups/smsapp_\$(date +\%Y\%m\%d).sql") | crontab -
```

## Updating the Application

To update the application:

```bash
# Pull the latest code
git pull

# Rebuild and restart containers
docker-compose down
docker-compose build
docker-compose up -d
```

## Scaling Considerations

For higher loads, consider:
1. Setting up multiple web instances behind a load balancer
2. Moving the database to a managed service (like AWS RDS or DigitalOcean Managed Databases)
3. Setting up monitoring with Prometheus/Grafana

## Troubleshooting

### Connection Issues
- Check if all containers are running: `docker-compose ps`
- Verify Nginx configuration: `docker exec -it quantum-hub-sms_nginx_1 nginx -t`
- Check logs: `docker-compose logs nginx` or `docker-compose logs web`

### Database Issues
- Connect to the database: `docker exec -it quantum-hub-sms_db_1 psql -U postgres -d smsapp`
- Check database tables: `\dt` (in psql)

## Security Best Practices

1. Keep your server updated
2. Use strong passwords
3. Set up a firewall:
   ```
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```
4. Consider setting up fail2ban
5. Regularly backup your data

For additional support, please contact the development team. 