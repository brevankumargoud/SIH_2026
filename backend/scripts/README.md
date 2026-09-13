# Backend Scripts

## Development User Provisioning

To create a local development user and bypass the need for an external registration flow, use the `create_dev_user.py` script. 

This tool interactively prompts for user credentials, securely hashes the password using Argon2, and provisions the user with proper Role-Based Access Control assignments in your local PostgreSQL database. 

**Note**: This script is strictly for local development and will refuse to run if `ENVIRONMENT=production`.

### Usage

1. Ensure your virtual environment is activated and dependencies are installed.
2. Run the script:

```bash
python scripts/create_dev_user.py
```

To automatically pre-select a specific role, you can optionally pass the `--role` flag:

```bash
python scripts/create_dev_user.py --role user
```

You will be prompted for:
- Username
- Email address
- Full Name (optional)
- Password (hidden input)
- Confirm Password (hidden input)
- Role assignment

Once created, the resulting user can authenticate normally via the standard `POST /auth/login` API endpoint in both the FastAPI backend and Next.js frontend.
