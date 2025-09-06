// Функции для работы с выбором даты бронирования
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('booking_date');
    const endDateElement = document.getElementById('end_date_display');
    
    if (dateInput) {
        // Функция для расчета даты окончания
        function updateEndDate() {
            if (dateInput.value) {
                const startDate = new Date(dateInput.value);
                const endDate = new Date(startDate);
                endDate.setDate(startDate.getDate() + 14);
                
                const options = { day: 'numeric', month: 'long', year: 'numeric' };
                const endDateFormatted = endDate.toLocaleDateString('ru-RU', options);
                
                if (endDateElement) {
                    endDateElement.textContent = endDateFormatted;
                } else {
                    // Создаем элемент для отображения даты окончания
                    const endDateDiv = document.createElement('div');
                    endDateDiv.className = 'end-date-info';
                    endDateDiv.innerHTML = `<strong>Дата окончания брони:</strong> ${endDateFormatted}`;
                    endDateDiv.style.marginTop = '10px';
                    endDateDiv.style.padding = '10px';
                    endDateDiv.style.backgroundColor = '#e8f4f8';
                    endDateDiv.style.borderRadius = '5px';
                    
                    dateInput.parentNode.appendChild(endDateDiv);
                }
            }
        }
        
        // Обновляем при изменении даты
        dateInput.addEventListener('change', updateEndDate);
        
        // Обновляем при загрузке
        updateEndDate();
    }
});