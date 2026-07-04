# 📰 Fake News Detection System

A web-based Fake News Detection application that uses Machine Learning and Natural Language Processing (NLP) to classify news articles as **Real** or **Fake**. The application provides a simple interface where users can enter news content and receive instant predictions.

---

## 🚀 Features

- Detects whether news is Real or Fake
- User-friendly web interface
- Machine Learning-based prediction
- Fast and accurate results
- Responsive design
- Easy to deploy

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Machine Learning
- Scikit-learn
- Pandas
- NumPy
- NLTK
- TF-IDF Vectorizer

---

## 📁 Project Structure

```
backend/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── login.html
│
├── app.py
├── model.pkl
├── vectorizer.pkl
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

1. Clone the repository

```bash
git clone https://github.com/your-username/FAKE-NEWS-APP.git
```

2. Move into the project directory

```bash
cd FAKE-NEWS-APP
```

3. Create a virtual environment (Optional)

```bash
python -m venv venv
```

4. Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

5. Install dependencies

```bash
pip install -r requirements.txt
```

6. Run the application

```bash
python app.py
```

7. Open your browser

```
http://127.0.0.1:5000
```

---

## 📖 How It Works

1. Enter a news article.
2. The text is preprocessed using NLP.
3. TF-IDF converts the text into numerical features.
4. The trained Machine Learning model predicts the result.
5. The application displays whether the news is **Real** or **Fake**.

---

## 📸 Screenshots

Add screenshots of your application here.

---

## 🎯 Future Enhancements

- User authentication
- News history
- Confidence score
- Multiple language support
- AI-powered explanation for predictions
- REST API integration

---

## 👨‍💻 Author

"M.chandru"

---

## 📄 License

This project is intended for finding Real news or Fake news.
