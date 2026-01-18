@echo off
echo ========================================
echo Push Phase 5 Code to GitHub
echo ========================================
echo.

echo [1/6] Checking current branch...
git branch --show-current

echo.
echo [2/6] Checking git status...
git status

echo.
echo [3/6] Adding all Phase 5 changes...
git add .

echo.
echo [4/6] Creating commit...
git commit -m "feat(phase-5): complete production deployment to DigitalOcean DOKS

- Fixed frontend auto-login after signup (no email verification)
- Fixed backend CORS to allow production domain
- Added Kubernetes production manifests (namespace, deployments, services, ingress)
- Configured DigitalOcean Container Registry integration
- Set up Nginx ingress controller with LoadBalancer
- Added environment variables for production API URLs
- Fixed middleware to use internal Kubernetes service URLs
- Created deployment scripts and documentation
- Added comprehensive testing and diagnostic tools

Deployed at: http://161-35-250-151.nip.io

Tech Stack:
- Frontend: Next.js 14, deployed on DOKS
- Backend: FastAPI, deployed on DOKS
- Database: Neon Serverless PostgreSQL
- Infrastructure: DigitalOcean Kubernetes (2 nodes)
- Container Registry: DigitalOcean CR (500MB)
- Ingress: Nginx with nip.io wildcard DNS

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

echo.
echo [5/6] Pushing to GitHub...
git push origin 004-ai-chatbot

echo.
echo [6/6] Creating GitHub release tag...
git tag -a v1.0.0-phase5 -m "Phase 5: Production Deployment to DigitalOcean DOKS"
git push origin v1.0.0-phase5

echo.
echo ========================================
echo Code Pushed Successfully!
echo ========================================
echo.
echo Your code is now on GitHub with:
echo   ✓ All Phase 5 changes
echo   ✓ Kubernetes manifests
echo   ✓ PHRs (if they exist in history/prompts/)
echo   ✓ Documentation
echo   ✓ Release tag v1.0.0-phase5
echo.
echo Next: Create a README update with production URL
echo.
pause
