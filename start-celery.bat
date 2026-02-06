@echo off
echo ========================================
echo   Celery Services Startup Script
echo ========================================
echo.

echo [1/3] Starting Celery Worker...
start "Celery Worker" cmd /k "cd /d p:\workspace\blog\backend && python -m celery -A config worker -l info --pool=solo"
timeout /t 3 >nul

echo [2/3] Starting Celery Beat...
start "Celery Beat" cmd /k "cd /d p:\workspace\blog\backend && python -m celery -A config beat -l info"
timeout /t 2 >nul

echo [3/3] Starting Flower Monitor...
start "Flower Monitor" cmd /k "cd /d p:\workspace\blog\backend && python -m celery -A config flower"

echo.
echo ========================================
echo   All Celery services started!
echo ========================================
echo.
echo Services:
echo   - Worker:  Processing tasks
echo   - Beat:    Scheduling periodic tasks
echo   - Flower:  http://localhost:5555
echo.
echo Scheduled Tasks:
echo   - Daily Statistics:     00:00 every day
echo   - Clean Cache:           Every hour
echo   - Popular Articles:     Every 15 minutes
echo.
pause
