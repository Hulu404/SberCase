# 🧠 Ника by AI-Болит | Телеграм-бот ментальной поддержки и сопровождения спортсменов

![Логотип](https://via.placeholder.com/100x100/4285F4/FFFFFF?text=🧠)  
*Ваш цифровой помощник для заботы о ментальном здоровье*

---

## 🎯 Задачи проекта

- ✅ Предоставление анонимной психологической поддержки
- ✅ Ежедневные проверки настроения (mood tracking)
- ✅ Библиотека техник саморегуляции и медитаций
- ✅ Тревожная кнопка для экстренных случаев
- ✅ Персональные рекомендации контента
- ✅ Интеграция с календарем для формирования привычек

---

## 📁 Структура проекта

<details>
<summary><strong>Развернуть структуру проекта</strong></summary>
  
```bash
mind-support-bot/
├── src/ 
│   ├── bot/
│   │   ├── __init__.py  
│   │   ├── core.py # Основная логика бота  
│   │   ├── handlers/ # Обработчики сообщений  
│   │   │   ├── common.py  
│   │   │   ├── support.py  
│   │   │   └── exercises.py  
│   │   └── keyboards.py # Клавиатуры и кнопки  
│   ├── database/  
│   │   ├── models.py # Модели данных  
│   │   └── crud.py # Операции с БД  
│   ├── utils/ 
│   │   ├── helpers.py # Вспомогательные функции  
│   │   └── content_loader.py # Загрузчик контента  
│   └── config.py # Конфигурация  
├── data/  
│   ├── exercises/ # Медитации и упражнения  
│   └── phrases.json # Поддерживающие фразы  
├── tests/  
├── requirements.txt  
└── README.md
```
</details>

---

## 💻 Технологический Stack

<details>
  <summary><strong>Развернуть технологический стэк</strong></summary>

### 1. Core Technologies:
  * **PyTorch**:
    * Implemented **RNN/LSTM/GRU** for time-series or sequential data.
    * Utilized automatic differentiation (autograd).
    * GPU (CUDA) support for accelerated training.
  * **Python**: Primary programming language.
### 2. **Data Processing**:
  * Data Sources:
      - Parkinson’s disease datasets (e.g., UCI Machine Learning Repository, Physionet).
      - Formats: CSV, sensor time-series. 
  * Data Processing Libraries:
     * **Pandas**: Data loading, cleaning, and preprocessing.
     * **NumPy**: Handling multidimensional arrays.
     * **Scikit-learn**:
       * Normalization/scaling (MinMaxScaler, RobustScaler StandardScaler).
       * Train/validation/test split.
       * Evaluation metrics (accuracy, F1-score, ROC-AUC).
### 3. **Model Architecture**:
  * Neural Network Layers:
      * Recurrent layers (RNN, LSTM, GRU).
      * Fully connected layers (Linear).
      * Regularization: Dropout, BatchNorm.
  * Activation Functions: ReLU, Sigmoid, Softmax.
### 4. **Development Tools**:
  * Version Control: Git + GitHub/GitLab.
  * IDE: Jupyter Notebook, PyCharm.
</details>

---

