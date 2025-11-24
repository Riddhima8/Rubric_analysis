# 🎤 AI Self-Introduction Scorer

A premium **Streamlit web app** that evaluates a spoken or written self-introduction using a **strict Excel-style rubric**, providing:

✅ Scoring out of 100
✅ Category-level feedback
✅ Grammar & vocabulary evaluation
✅ Engagement & sentiment scoring
✅ Flow & structure analysis
✅ Premium UI with gauge, cards, tabs, and confetti

This tool is ideal for:
- Students practicing introductions
- Teachers evaluating presentation skills
- Public speaking training
- Soft skills assessment platforms

---

## 🚀 Live Demo (Optional)
Add your Streamlit Cloud / HuggingFace / Render link here:

```
https://your-deployment-link
```

---

## 🧠 Features

### ✅ Strict Rubric-Based Scoring (No AI Bias)
Score is calculated using a fixed rubric:
- Content & Structure (40)
- Speech Rate (10)
- Grammar (10)
- Vocabulary (10)
- Clarity (15)
- Engagement (15)

### ✅ Premium UI
Includes:
- Gauge dial score visualization
- Category score cards
- Tabs for navigation
- Progress bars
- Confetti animation (score ≥ 85)
- Clean modern layout

---

## 🏗️ Tech Stack

- Python 3
- Streamlit
- VADER Sentiment Analysis
- LanguageTool (Grammar Checking)
- Plotly (Gauge visualization)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/self-intro-scorer.git
cd self-intro-scorer
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

Then open:
```
http://localhost:8501
```

---

## 📁 Project Structure

```
📦 self-intro-scorer
├── app.py
├── requirements.txt
├── README.md
└── assets/ (optional)
```

---

## 📝 How Scoring Works

The rubric identifies:

### Must-Have Elements (20 pts)
✅ Name
✅ Age
✅ Class/School
✅ Family
✅ Hobbies

### Good-to-Have Elements (10 pts)
✅ Origin
✅ Ambition/Goal
✅ About family
✅ Interesting fact
✅ Achievements

### Flow (5 pts)
Correct sequence:
Salutation → Basic Details → Additional Details → Closing

### Grammar (10 pts)
Uses LanguageTool to count errors

### Vocabulary (10 pts)
Uses TTR (type-token ratio)

### Clarity (15 pts)
Detects filler words

### Engagement (15 pts)
Sentiment score from VADER

---

## ✅ Example Input

```
Good morning everyone,
My name is Rahul. I am 12 years old...
```

### ✅ Example Output
```
Overall Score: 80 / 100
```

---

## ✅ Screenshot
(Add a screenshot of your UI here)

```
![App Screenshot](assets/screenshot.png)
```

---

## 🌟 Future Improvements

- Voice recording input
- Automatic speech-to-text
- PDF report generation
- User history dashboard

---

## 🤝 Contributing
Pull requests are welcome!

---

## 🧑‍💻 Author
Your Name

---

## 📜 License
MIT License

