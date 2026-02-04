@echo off
echo ========================================
echo Запуск приложения FindCar
echo ========================================
echo.

if not exist "venv\" (
    echo ОШИБКА: Виртуальное окружение не найдено!
    echo Сначала запустите setup.bat
    echo.
    pause
    exit /b 1
)

echo Активация виртуального окружения...
call venv\Scripts\activate.bat
echo.

echo Запуск Flask приложения...
echo Приложение будет доступно по адресу: http://localhost:5000
echo.
echo Для остановки нажмите Ctrl+C
echo.
python app.py
