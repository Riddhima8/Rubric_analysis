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

## ✅ Screenshots


```
<img width="1184" height="726" alt="image" src="https://github.com/user-attachments/assets/15f842f6-3540-458e-a70d-2b9e193a6075" />
<img width="958" height="443" alt="image" src="https://github.com/user-attachments/assets/2c25537f-61a1-4863-a020-77db93fbeca5" />
<img width="1218" height="809" alt="image" src="https://github.com/user-attachments/assets/5307d63c-063a-468d-9a8e-94a826dd934f" />
<img width="935" height="827" alt="image" src="https://github.com/user-attachments/assets/65846e44-b3b4-4335-937e-5c4896ef67af" />
<img width="1021" height="772" alt="image" src="https://github.com/user-attachments/assets/75b02b25-30e7-41c0-9296-5b5815746905" />

```

---

## 🌟 Future Improvements

- Voice recording input
- Automatic speech-to-text
- PDF report generation
- User history dashboard
- Deployment

---



