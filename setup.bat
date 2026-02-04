@echo off
echo ========================================
echo Настройка виртуального окружения
echo ========================================
echo.

echo [1/3] Создание виртуального окружения...
python -m venv venv
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось создать venv
    pause
    exit /b 1
)
echo Готово!
echo.

echo [2/3] Активация виртуального окружения...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось активировать venv
    pause
    exit /b 1
)
echo Готово!
echo.

echo [3/3] Установка зависимостей...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости
    pause
    exit /b 1
)
echo Готово!
echo.

echo ========================================
echo Установка завершена успешно!
echo ========================================
echo.
echo Для запуска приложения используйте: run.bat
echo.
pause
