# Deploy to Amazon EC2

These instructions deploy the Flask app on an Ubuntu EC2 instance with Gunicorn, Nginx, and HTTPS.

## 1. Prepare the EC2 instance

In the EC2 console, use an Ubuntu Server 22.04 or 24.04 instance. In its security group, allow:

| Type | Port | Source |
| --- | ---: | --- |
| SSH | 22 | Your current public IP only |
| HTTP | 80 | Anywhere (`0.0.0.0/0`, and `::/0` if using IPv6) |
| HTTPS | 443 | Anywhere (`0.0.0.0/0`, and `::/0` if using IPv6) |

Do not expose ports 5000 or 8000 publicly. Flask's development server and Gunicorn will not be directly internet-facing.

The server address for this deployment is `18.222.162.234`. Confirm it is an Elastic IP associated with this instance before configuring DNS. A regular EC2 public IPv4 address can change when the instance is stopped and started.

## 2. Point the domain to EC2

At your DNS provider, create these records:

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `18.222.162.234` |
| A | `www` | `18.222.162.234` |

Wait for DNS to propagate, then confirm that `pythonappquantplux.com` and `www.pythonappquantplux.com` resolve to the EC2 address. If you do not want the `www` hostname, omit its record and remove it from the Nginx and Certbot commands below.

## 3. Connect and install packages

From PowerShell, replace the key path with the path to your EC2 private key:

```powershell
ssh -i "C:\path\to\your-key.pem" ubuntu@18.222.162.234
```

On the EC2 instance, install system packages and prepare the application directory:

```bash
sudo apt update
sudo apt install -y git nginx python3-venv python3-pip
sudo mkdir -p /opt/random-quote-generator-python-app
sudo chown ubuntu:ubuntu /opt/random-quote-generator-python-app
```

Clone the repository into the empty directory. Replace the URL with the HTTPS or SSH clone URL for this repository:

```bash
git clone <YOUR_REPOSITORY_URL> /opt/random-quote-generator-python-app
cd /opt/random-quote-generator-python-app
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt gunicorn
```

If the GitHub repository is private, configure a deploy key or another non-interactive read-only authentication method before cloning.

## 4. Configure the Flask secret

Generate a strong secret on the EC2 instance:

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

Create a root-readable environment file with the generated value:

```bash
sudo nano /etc/random-quote-generator.env
```

Add this line, replacing the placeholder with the generated secret:

```text
SECRET_KEY=replace-with-the-generated-secret
```

Save the file, then restrict access:

```bash
sudo chmod 600 /etc/random-quote-generator.env
```

Keep this secret out of Git and do not use the development fallback secret for production.

## 5. Run Gunicorn with systemd

Create the service file:

```bash
sudo nano /etc/systemd/system/random-quote-generator.service
```

Paste this configuration:

```ini
[Unit]
Description=Random Quote Generator Flask application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/random-quote-generator-python-app
EnvironmentFile=/etc/random-quote-generator.env
ExecStart=/opt/random-quote-generator-python-app/.venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start the service, then check its status:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now random-quote-generator
sudo systemctl status random-quote-generator
```

If it does not start, inspect the service log:

```bash
sudo journalctl -u random-quote-generator -n 50 --no-pager
```

## 6. Configure Nginx

Create an Nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/random-quote-generator
```

Add:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name pythonappquantplux.com www.pythonappquantplux.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and validate the configuration before reloading Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/random-quote-generator /etc/nginx/sites-enabled/random-quote-generator
sudo nginx -t
sudo systemctl reload nginx
```

## 7. Enable HTTPS

Once both domain names resolve to the instance and ports 80 and 443 are open in the EC2 security group, install Certbot and request the certificate:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d pythonappquantplux.com -d www.pythonappquantplux.com
```

Follow Certbot's prompts to provide an email address and enable HTTP-to-HTTPS redirection. Test automatic renewal:

```bash
sudo certbot renew --dry-run
```

## 8. Verify and update

Visit `https://pythonappquantplux.com` and refresh the page to confirm the quote changes. You can also check the response from the instance:

```bash
curl -I https://pythonappquantplux.com
```

For a later deployment, pull the latest code and restart the service:

```bash
cd /opt/random-quote-generator-python-app
git pull
.venv/bin/pip install -r requirements.txt gunicorn
sudo systemctl restart random-quote-generator
```