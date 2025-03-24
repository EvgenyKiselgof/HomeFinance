import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from datetime import datetime, timedelta
import calendar
import plotly.graph_objects as go
import plotly.express as px
import random
import io
import base64

# הגדרת מבנה האפליקציה
st.set_page_config(
    page_title="RiseUp - ניהול תקציב ביתי",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# סטיילינג בסיסי
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1565C0;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .income {
        color: #2E7D32;
        font-weight: bold;
    }
    .expense {
        color: #C62828;
        font-weight: bold;
    }
    .chart-container {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        background-color: #f5f5f5;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stButton>button {
        background-color: #1565C0;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# אתחול משתני סשן
def init_session_state():
    if 'transactions' not in st.session_state:
        # טבלת עסקאות
        st.session_state.transactions = pd.DataFrame({
            'id': [],
            'date': [],
            'amount': [],
            'category': [],
            'description': [],
            'type': []  # 'income' או 'expense'
        })

    if 'categories' not in st.session_state:
        # קטגוריות הוצאות והכנסות
        st.session_state.categories = {
            'income': ['משכורת', 'בונוס', 'מתנות', 'השקעות', 'שכר דירה', 'אחר'],
            'expense': ['מזון', 'דיור', 'חשבונות', 'תחבורה', 'בידור', 'בריאות',
                        'ביגוד', 'חינוך', 'חיסכון', 'חופשות', 'קניות', 'אחר']
        }

    if 'budgets' not in st.session_state:
        # תקציב לפי קטגוריה
        st.session_state.budgets = {category: 0 for category in st.session_state.categories['expense']}

    if 'view' not in st.session_state:
        # דף נוכחי
        st.session_state.view = 'סקירה'

    if 'month_filter' not in st.session_state:
        # חודש לסינון נתונים
        current_month = datetime.now().month
        current_year = datetime.now().year
        st.session_state.month_filter = f"{current_year}-{current_month:02d}"

    if 'show_sample_data' not in st.session_state:
        # האם להציג נתונים לדוגמה
        st.session_state.show_sample_data = False


# יצירת מזהה ייחודי לכל עסקה
def generate_id():
    return random.randint(10000, 99999)


# פונקציה לטעינת נתונים לדוגמה
def load_sample_data():
    if st.session_state.show_sample_data:
        return

    st.session_state.show_sample_data = True

    # יצירת תאריכים לחודש נוכחי
    current_month = datetime.now().month
    current_year = datetime.now().year
    days_in_month = calendar.monthrange(current_year, current_month)[1]

    # נתוני הכנסות לדוגמה
    income_data = [
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 10),
            'amount': 12000,
            'category': 'משכורת',
            'description': 'משכורת חודשית',
            'type': 'income'
        },
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 15),
            'amount': 2500,
            'category': 'שכר דירה',
            'description': 'הכנסה מהשכרת חדר',
            'type': 'income'
        },
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 20),
            'amount': 500,
            'category': 'השקעות',
            'description': 'דיבידנדים',
            'type': 'income'
        }
    ]

    # נתוני הוצאות לדוגמה
    expense_data = [
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 1),
            'amount': 3500,
            'category': 'דיור',
            'description': 'שכר דירה',
            'type': 'expense'
        },
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 5),
            'amount': 800,
            'category': 'חשבונות',
            'description': 'חשמל ומים',
            'type': 'expense'
        },
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 8),
            'amount': 1200,
            'category': 'מזון',
            'description': 'קניות סופר שבועיות',
            'type': 'expense'
        },
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 12),
            'amount': 400,
            'category': 'תחבורה',
            'description': 'דלק',
            'type': 'expense'
        },
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 15),
            'amount': 350,
            'category': 'בידור',
            'description': 'מסעדה',
            'type': 'expense'
        },
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 18),
            'amount': 200,
            'category': 'בריאות',
            'description': 'תרופות',
            'type': 'expense'
        },
        {
            'id': generate_id(),
            'date': datetime(current_year, current_month, 22),
            'amount': 500,
            'category': 'קניות',
            'description': 'ביגוד',
            'type': 'expense'
        }
    ]

    # הגדרת תקציבים לדוגמה
    budgets = {
        'מזון': 2000,
        'דיור': 4000,
        'חשבונות': 1000,
        'תחבורה': 700,
        'בידור': 1000,
        'בריאות': 500,
        'ביגוד': 700,
        'חינוך': 300,
        'חיסכון': 1500,
        'חופשות': 1000,
        'קניות': 800,
        'אחר': 500
    }

    # עדכון תקציבים
    st.session_state.budgets = budgets

    # הוספת עסקאות לטבלה
    sample_data = pd.DataFrame(income_data + expense_data)
    st.session_state.transactions = pd.concat([st.session_state.transactions, sample_data], ignore_index=True)


# פונקציה לסינון עסקאות לפי חודש
def filter_transactions_by_month(month_str):
    transactions = st.session_state.transactions

    if len(transactions) == 0:
        return pd.DataFrame({
            'id': [],
            'date': [],
            'amount': [],
            'category': [],
            'description': [],
            'type': []
        })

    year, month = map(int, month_str.split('-'))
    mask = (transactions['date'].dt.year == year) & (transactions['date'].dt.month == month)
    return transactions[mask]


# פונקציה לחישוב סיכומים חודשיים
def calculate_monthly_summary(filtered_transactions):
    if len(filtered_transactions) == 0:
        return {
            'total_income': 0,
            'total_expenses': 0,
            'net_savings': 0,
            'income_by_category': {},
            'expenses_by_category': {},
            'savings_rate': 0
        }

    # סיכום הכנסות והוצאות
    income = filtered_transactions[filtered_transactions['type'] == 'income']
    expenses = filtered_transactions[filtered_transactions['type'] == 'expense']

    total_income = income['amount'].sum() if len(income) > 0 else 0
    total_expenses = expenses['amount'].sum() if len(expenses) > 0 else 0
    net_savings = total_income - total_expenses

    # חישוב לפי קטגוריה
    income_by_category = income.groupby('category')['amount'].sum().to_dict() if len(income) > 0 else {}
    expenses_by_category = expenses.groupby('category')['amount'].sum().to_dict() if len(expenses) > 0 else {}

    # אחוז חיסכון
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'income_by_category': income_by_category,
        'expenses_by_category': expenses_by_category,
        'savings_rate': savings_rate
    }


# פונקציה להשוואת תקציב מול הוצאות בפועל
def calculate_budget_vs_actual(filtered_transactions):
    if len(filtered_transactions) == 0:
        return pd.DataFrame({
            'category': st.session_state.categories['expense'],
            'budget': [st.session_state.budgets.get(cat, 0) for cat in st.session_state.categories['expense']],
            'actual': [0] * len(st.session_state.categories['expense']),
            'diff': [0] * len(st.session_state.categories['expense']),
            'perc_used': [0] * len(st.session_state.categories['expense'])
        })

    # סינון רק הוצאות
    expenses = filtered_transactions[filtered_transactions['type'] == 'expense']
    expenses_by_category = expenses.groupby('category')['amount'].sum().to_dict() if len(expenses) > 0 else {}

    # יצירת טבלת השוואה
    comparison = []
    for category in st.session_state.categories['expense']:
        budget = st.session_state.budgets.get(category, 0)
        actual = expenses_by_category.get(category, 0)
        diff = budget - actual
        perc_used = (actual / budget * 100) if budget > 0 else 0

        comparison.append({
            'category': category,
            'budget': budget,
            'actual': actual,
            'diff': diff,
            'perc_used': perc_used
        })

    return pd.DataFrame(comparison)


# פונקציה ליצירת תרשים הוצאות לפי קטגוריה
def create_expenses_by_category_chart(filtered_transactions):
    if len(filtered_transactions) == 0:
        return None

    expenses = filtered_transactions[filtered_transactions['type'] == 'expense']
    if len(expenses) == 0:
        return None

    # חישוב סכום לפי קטגוריה
    expenses_by_category = expenses.groupby('category')['amount'].sum().reset_index()

    # יצירת תרשים עוגה
    fig = px.pie(
        expenses_by_category,
        values='amount',
        names='category',
        title='התפלגות הוצאות לפי קטגוריה',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')

    return fig


# פונקציה ליצירת תרשים מגמה חודשית
def create_monthly_trend_chart():
    transactions = st.session_state.transactions

    if len(transactions) == 0:
        return None

    # הוספת עמודות שנה וחודש
    transactions['year_month'] = transactions['date'].dt.strftime('%Y-%m')

    # סיכום לפי חודש וסוג עסקה
    monthly_income = transactions[transactions['type'] == 'income'].groupby('year_month')['amount'].sum()
    monthly_expenses = transactions[transactions['type'] == 'expense'].groupby('year_month')['amount'].sum()
    monthly_savings = monthly_income.subtract(monthly_expenses, fill_value=0)

    # יצירת דאטאפריים מסוכם
    summary_df = pd.DataFrame({
        'income': monthly_income,
        'expenses': monthly_expenses,
        'savings': monthly_savings
    }).reset_index()

    # מיון לפי תאריך
    summary_df = summary_df.sort_values('year_month')

    if len(summary_df) == 0:
        return None

    # יצירת תרשים קווי
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=summary_df['year_month'],
        y=summary_df['income'],
        name='הכנסות',
        line=dict(color='#2E7D32', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=summary_df['year_month'],
        y=summary_df['expenses'],
        name='הוצאות',
        line=dict(color='#C62828', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=summary_df['year_month'],
        y=summary_df['savings'],
        name='חסכונות',
        line=dict(color='#1565C0', width=3, dash='dot')
    ))

    fig.update_layout(
        title='מגמות הכנסות, הוצאות וחסכונות לאורך זמן',
        xaxis_title='חודש',
        yaxis_title='סכום (₪)',
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    return fig


# פונקציה ליצירת תרשים השוואת תקציב מול ביצוע
def create_budget_vs_actual_chart(budget_comparison):
    if len(budget_comparison) == 0:
        return None

    # סינון רק קטגוריות עם תקציב או הוצאות
    df = budget_comparison[(budget_comparison['budget'] > 0) | (budget_comparison['actual'] > 0)]

    if len(df) == 0:
        return None

    # יצירת תרשים עמודות
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['category'],
        y=df['budget'],
        name='תקציב',
        marker_color='#1565C0'
    ))

    fig.add_trace(go.Bar(
        x=df['category'],
        y=df['actual'],
        name='הוצאות בפועל',
        marker_color='#C62828'
    ))

    fig.update_layout(
        title='השוואת תקציב מול ביצוע',
        xaxis_title='קטגוריה',
        yaxis_title='סכום (₪)',
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    return fig


# פונקציה ליצירת קובץ CSV להורדה
def download_csv(filtered_transactions):
    if len(filtered_transactions) == 0:
        return None

    # עיבוד נתונים לפני הורדה
    df = filtered_transactions.copy()
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')  # המרת תאריך לפורמט מתאים

    # יצירת קובץ CSV
    csv = df.to_csv(index=False, encoding='utf-8-sig')

    # קידוד ב-Base64 לשימוש בקישור להורדה
    b64 = base64.b64encode(csv.encode()).decode()

    # יצירת קישור להורדה
    href = f'<a href="data:file/csv;base64,{b64}" download="transactions.csv" class="download-link">הורד נתונים כקובץ CSV</a>'

    return href


# אתחול מצב הסשן
init_session_state()

# יצירת סרגל צד
with st.sidebar:
    st.markdown('<h1 class="main-header">RiseUp</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">ניהול תקציב ביתי חכם</p>', unsafe_allow_html=True)

    # כפתורי ניווט
    if st.button('🏠 סקירה'):
        st.session_state.view = 'סקירה'

    if st.button('📊 דוחות'):
        st.session_state.view = 'דוחות'

    if st.button('💰 הכנסה חדשה'):
        st.session_state.view = 'הכנסה חדשה'

    if st.button('💸 הוצאה חדשה'):
        st.session_state.view = 'הוצאה חדשה'

    if st.button('⚙️ הגדרות תקציב'):
        st.session_state.view = 'הגדרות תקציב'

    if st.button('📝 עסקאות'):
        st.session_state.view = 'עסקאות'

    st.markdown('---')

    # בחירת חודש
    year_month = st.text_input('חודש נוכחי (YYYY-MM)', value=st.session_state.month_filter)
    if year_month != st.session_state.month_filter:
        try:
            # בדיקת תקינות הפורמט
            year, month = map(int, year_month.split('-'))
            if 1 <= month <= 12 and 2000 <= year <= 2100:
                st.session_state.month_filter = year_month
        except:
            st.error('פורמט לא תקין. השתמש בפורמט YYYY-MM')

    st.markdown('---')

    # טעינת נתוני דוגמה
    if not st.session_state.show_sample_data:
        if st.button('טען נתוני דוגמה'):
            load_sample_data()
            st.success('נתוני דוגמה נטענו בהצלחה!')

# סינון עסקאות לפי החודש הנבחר
filtered_transactions = filter_transactions_by_month(st.session_state.month_filter)

# חישוב סיכומים חודשיים
monthly_summary = calculate_monthly_summary(filtered_transactions)

# חישוב השוואת תקציב מול ביצוע
budget_comparison = calculate_budget_vs_actual(filtered_transactions)

# דף סקירה
if st.session_state.view == 'סקירה':
    st.markdown('<h1 class="main-header">סקירה חודשית</h1>', unsafe_allow_html=True)

    # הצגת חודש נוכחי
    year, month = map(int, st.session_state.month_filter.split('-'))
    month_name = calendar.month_name[month]
    st.markdown(f'<h2 class="sub-header">{month_name} {year}</h2>', unsafe_allow_html=True)

    # כרטיסי מדדים
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("סה\"כ הכנסות", f"{monthly_summary['total_income']:,.0f} ₪")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("סה\"כ הוצאות", f"{monthly_summary['total_expenses']:,.0f} ₪")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        net_savings = monthly_summary['net_savings']
        delta_color = "normal" if net_savings >= 0 else "inverse"
        st.metric("חיסכון נטו", f"{net_savings:,.0f} ₪", delta_color=delta_color)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        savings_rate = monthly_summary['savings_rate']
        st.metric("אחוז חיסכון", f"{savings_rate:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    # תרשימים
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        expenses_chart = create_expenses_by_category_chart(filtered_transactions)
        if expenses_chart:
            st.plotly_chart(expenses_chart, use_container_width=True)
        else:
            st.info("אין נתונים להצגת התפלגות הוצאות")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        budget_chart = create_budget_vs_actual_chart(budget_comparison)
        if budget_chart:
            st.plotly_chart(budget_chart, use_container_width=True)
        else:
            st.info("אין נתונים להשוואת תקציב מול ביצוע")
        st.markdown('</div>', unsafe_allow_html=True)

    # תרשים מגמות חודשיות
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    trend_chart = create_monthly_trend_chart()
    if trend_chart:
        st.plotly_chart(trend_chart, use_container_width=True)
    else:
        st.info("אין מספיק נתונים להצגת מגמות חודשיות")
    st.markdown('</div>', unsafe_allow_html=True)

    # הצגת עסקאות אחרונות
    st.markdown('<h2 class="sub-header">עסקאות אחרונות</h2>', unsafe_allow_html=True)

    if len(filtered_transactions) > 0:
        # מיון לפי תאריך, מהחדש לישן
        recent_transactions = filtered_transactions.sort_values('date', ascending=False).head(5)

        for _, transaction in recent_transactions.iterrows():
            transaction_type = "income" if transaction['type'] == 'income' else "expense"
            amount_text = f"+{transaction['amount']:,.0f} ₪" if transaction[
                                                                    'type'] == 'income' else f"-{transaction['amount']:,.0f} ₪"

            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <strong>{transaction['description']}</strong>
                        <br>
                        <small>{transaction['category']} • {transaction['date'].strftime('%d/%m/%Y')}</small>
                    </div>
                    <div class="{transaction_type}">{amount_text}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("אין עסקאות להצגה בחודש זה")

# דף דוחות
elif st.session_state.view == 'דוחות':
    st.markdown('<h1 class="main-header">דוחות וניתוחים</h1>', unsafe_allow_html=True)

    # הצגת חודש נוכחי
    year, month = map(int, st.session_state.month_filter.split('-'))
    month_name = calendar.month_name[month]
    st.markdown(f'<h2 class="sub-header">{month_name} {year}</h2>', unsafe_allow_html=True)

    # בחירת סוג דוח
    report_type = st.radio(
        "בחר סוג דוח:",
        ["השוואת תקציב מול ביצוע", "התפלגות הוצאות", "מגמות לאורך זמן", "ניתוח הכנסות"]
    )

    if report_type == "השוואת תקציב מול ביצוע":
        st.markdown('<h3 class="sub-header">השוואת תקציב מול ביצוע</h3>', unsafe_allow_html=True)

        # תרשים השוואת תקציב
        budget_chart = create_budget_vs_actual_chart(budget_comparison)
        if budget_chart:
            st.plotly_chart(budget_chart, use_container_width=True)

        # טבלת השוואה
        if len(budget_comparison) > 0:
            # הוספת עמודת אחוז ניצול תקציב
            styled_comparison = budget_comparison.copy()


            # הגדרת סגנון לטבלה עם צבעים
            def color_budget_status(val):
                if val > 100:
                    return 'background-color: #FFCDD2'  # אדום בהיר אם חרגנו מהתקציב
                elif val > 80:
                    return 'background-color: #FFF9C4'  # צהוב בהיר אם מתקרבים לגבול
                else:
                    return 'background-color: #C8E6C9'  # ירוק בהיר אם בסדר


            # עיצוב הטבלה
            st.dataframe(
                styled_comparison
                .style
                .format({
                    'budget': '{:,.0f} ₪',
                    'actual': '{:,.0f} ₪',
                    'diff': '{:,.0f} ₪',
                    'perc_used': '{:.1f}%'
                })
                .applymap(lambda x: 'color: #C62828' if x < 0 else 'color: #2E7D32', subset=['diff'])
                .applymap(color_budget_status, subset=['perc_used'])
                .set_properties(**{'text-align': 'center'})
                .hide_index()
                .set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold')]},
                ])
            )

            # המלצות על בסיס ניתוח התקציב
            st.markdown('<h4>המלצות חיסכון</h4>', unsafe_allow_html=True)

            # איתור קטגוריות שחרגו מהתקציב
            overspent = budget_comparison[budget_comparison['diff'] < 0].sort_values('diff')
            if len(overspent) > 0:
                st.warning(f"חרגת מהתקציב ב-{len(overspent)} קטגוריות:")
                for idx, row in overspent.iterrows():
                    st.markdown(
                        f"**{row['category']}**: חריגה של {-row['diff']:,.0f} ₪ ({row['perc_used']:.1f}% מהתקציב)")
            else:
                st.success("לא חרגת מהתקציב באף קטגוריה. כל הכבוד!")
        else:
            st.info("אין נתוני תקציב להצגה")

    elif report_type == "התפלגות הוצאות":
        st.markdown('<h3 class="sub-header">התפלגות הוצאות לפי קטגוריה</h3>', unsafe_allow_html=True)

        # תרשים עוגה של הוצאות
        expenses_chart = create_expenses_by_category_chart(filtered_transactions)
        if expenses_chart:
            st.plotly_chart(expenses_chart, use_container_width=True)

            # טבלת פירוט הוצאות
            expenses = filtered_transactions[filtered_transactions['type'] == 'expense']
            if len(expenses) > 0:
                expenses_by_category = expenses.groupby('category')['amount'].agg(['sum', 'count']).reset_index()
                expenses_by_category.columns = ['קטגוריה', 'סכום כולל', 'מספר עסקאות']
                expenses_by_category['אחוז מסך ההוצאות'] = expenses_by_category['סכום כולל'] / expenses_by_category[
                    'סכום כולל'].sum() * 100

                # מיון לפי סכום בסדר יורד
                expenses_by_category = expenses_by_category.sort_values('סכום כולל', ascending=False)

                # עיצוב הטבלה
                st.dataframe(
                    expenses_by_category
                    .style
                    .format({
                        'סכום כולל': '{:,.0f} ₪',
                        'אחוז מסך ההוצאות': '{:.1f}%'
                    })
                    .hide_index()
                )

                # קטגוריה עם ההוצאה הגבוהה ביותר
                top_category = expenses_by_category.iloc[0]['קטגוריה']
                top_amount = expenses_by_category.iloc[0]['סכום כולל']
                st.markdown(f"**ההוצאה הגבוהה ביותר:** {top_category} ({top_amount:,.0f} ₪)")
        else:
            st.info("אין נתוני הוצאות להצגה בחודש זה")

    elif report_type == "מגמות לאורך זמן":
        st.markdown('<h3 class="sub-header">מגמות לאורך זמן</h3>', unsafe_allow_html=True)

        # תרשים מגמות
        trend_chart = create_monthly_trend_chart()
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True)

            # ניתוח מגמות
            transactions = st.session_state.transactions

            if len(transactions) > 0:
                # הוספת עמודות שנה וחודש
                transactions['year_month'] = transactions['date'].dt.strftime('%Y-%m')

                # סיכום לפי חודש וסוג עסקה
                monthly_summary = []
                for ym in sorted(transactions['year_month'].unique()):
                    year, month = map(int, ym.split('-'))
                    month_trans = transactions[transactions['year_month'] == ym]

                    income = month_trans[month_trans['type'] == 'income']['amount'].sum()
                    expenses = month_trans[month_trans['type'] == 'expense']['amount'].sum()
                    savings = income - expenses
                    savings_rate = (savings / income * 100) if income > 0 else 0

                    monthly_summary.append({
                        'year_month': ym,
                        'income': income,
                        'expenses': expenses,
                        'savings': savings,
                        'savings_rate': savings_rate
                    })

                summary_df = pd.DataFrame(monthly_summary)

                if len(summary_df) > 1:
                    # מדדי שינוי בהשוואה לחודש קודם
                    latest = summary_df.iloc[-1]
                    previous = summary_df.iloc[-2]

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        income_change = ((latest['income'] - previous['income']) / previous['income'] * 100) if \
                        previous['income'] > 0 else 0
                        income_change_text = f"{income_change:+.1f}%" if previous['income'] > 0 else "אין נתון קודם"
                        st.metric("שינוי בהכנסות", f"{latest['income']:,.0f} ₪", income_change_text)

                    with col2:
                        expense_change = ((latest['expenses'] - previous['expenses']) / previous['expenses'] * 100) if \
                        previous['expenses'] > 0 else 0
                        expense_change_text = f"{expense_change:+.1f}%" if previous['expenses'] > 0 else "אין נתון קודם"
                        st.metric("שינוי בהוצאות", f"{latest['expenses']:,.0f} ₪", expense_change_text)

                    with col3:
                        savings_change = ((latest['savings'] - previous['savings']) / abs(previous['savings']) * 100) if \
                        previous['savings'] != 0 else 0
                        savings_change_text = f"{savings_change:+.1f}%" if previous['savings'] != 0 else "אין נתון קודם"
                        st.metric("שינוי בחיסכון", f"{latest['savings']:,.0f} ₪", savings_change_text)

                    # טבלת סיכום חודשי
                    st.markdown("<h4>סיכום חודשי</h4>", unsafe_allow_html=True)
                    st.dataframe(
                        summary_df
                        .style
                        .format({
                            'income': '{:,.0f} ₪',
                            'expenses': '{:,.0f} ₪',
                            'savings': '{:,.0f} ₪',
                            'savings_rate': '{:.1f}%'
                        })
                        .hide_index()
                    )
                else:
                    st.info("אין מספיק נתונים להשוואה בין חודשים")
        else:
            st.info("אין מספיק נתונים להצגת מגמות לאורך זמן")

    elif report_type == "ניתוח הכנסות":
        st.markdown('<h3 class="sub-header">ניתוח הכנסות</h3>', unsafe_allow_html=True)

        # סינון רק הכנסות
        incomes = filtered_transactions[filtered_transactions['type'] == 'income']

        if len(incomes) > 0:
            # תרשים התפלגות הכנסות
            income_by_category = incomes.groupby('category')['amount'].sum().reset_index()

            fig = px.pie(
                income_by_category,
                values='amount',
                names='category',
                title='התפלגות הכנסות לפי מקור',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')

            st.plotly_chart(fig, use_container_width=True)

            # טבלת פירוט הכנסות
            income_df = incomes[['date', 'amount', 'category', 'description']]
            income_df = income_df.sort_values('amount', ascending=False)

            st.markdown("<h4>פירוט הכנסות</h4>", unsafe_allow_html=True)
            st.dataframe(
                income_df
                .style
                .format({
                    'date': lambda x: x.strftime('%d/%m/%Y'),
                    'amount': '{:,.0f} ₪'
                })
                .hide_index()
            )

            # ניתוח הכנסות
            st.markdown("<h4>ניתוח הכנסות</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            * **סך כל ההכנסות:** {incomes['amount'].sum():,.0f} ₪
            * **מספר מקורות הכנסה:** {len(incomes['category'].unique())}
            * **הכנסה ממוצעת:** {incomes['amount'].mean():,.0f} ₪
            * **הכנסה הגבוהה ביותר:** {incomes['amount'].max():,.0f} ₪ ({incomes.loc[incomes['amount'].idxmax(), 'description']})
            """)
        else:
            st.info("אין נתוני הכנסות להצגה בחודש זה")

    # קישור להורדת נתונים
    st.markdown('---')
    if len(filtered_transactions) > 0:
        download_href = download_csv(filtered_transactions)
        st.markdown(download_href, unsafe_allow_html=True)

# דף הכנסה חדשה
elif st.session_state.view == 'הכנסה חדשה':
    st.markdown('<h1 class="main-header">הוספת הכנסה חדשה</h1>', unsafe_allow_html=True)

    with st.form("income_form"):
        # תאריך
        date = st.date_input("תאריך", value=datetime.now())

        # סכום
        amount = st.number_input("סכום (₪)", min_value=0.0, step=100.0)

        # קטגוריה
        category = st.selectbox("קטגוריה", st.session_state.categories['income'])

        # תיאור
        description = st.text_input("תיאור", placeholder="למשל: משכורת חודשית")

        # כפתור שמירה
        submitted = st.form_submit_button("הוסף הכנסה")

        if submitted:
            if amount <= 0:
                st.error("סכום ההכנסה חייב להיות גדול מאפס")
            elif not description:
                st.error("יש למלא תיאור")
            else:
                # הוספת עסקה חדשה
                new_transaction = pd.DataFrame({
                    'id': [generate_id()],
                    'date': [datetime.combine(date, datetime.min.time())],
                    'amount': [amount],
                    'category': [category],
                    'description': [description],
                    'type': ['income']
                })

                # הוספה לטבלת העסקאות
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction],
                                                          ignore_index=True)

                st.success(f"ההכנסה נוספה בהצלחה! סכום: {amount:,.0f} ₪")
                st.balloons()

# דף הוצאה חדשה
elif st.session_state.view == 'הוצאה חדשה':
    st.markdown('<h1 class="main-header">הוספת הוצאה חדשה</h1>', unsafe_allow_html=True)

    with st.form("expense_form"):
        # תאריך
        date = st.date_input("תאריך", value=datetime.now())

        # סכום
        amount = st.number_input("סכום (₪)", min_value=0.0, step=50.0)

        # קטגוריה
        category = st.selectbox("קטגוריה", st.session_state.categories['expense'])

        # תיאור
        description = st.text_input("תיאור", placeholder="למשל: קניות במרכול")

        # כפתור שמירה
        submitted = st.form_submit_button("הוסף הוצאה")

        if submitted:
            if amount <= 0:
                st.error("סכום ההוצאה חייב להיות גדול מאפס")
            elif not description:
                st.error("יש למלא תיאור")
            else:
                # הוספת עסקה חדשה
                new_transaction = pd.DataFrame({
                    'id': [generate_id()],
                    'date': [datetime.combine(date, datetime.min.time())],
                    'amount': [amount],
                    'category': [category],
                    'description': [description],
                    'type': ['expense']
                })

                # הוספה לטבלת העסקאות
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction],
                                                          ignore_index=True)

                # בדיקת חריגה מתקציב
                budget = st.session_state.budgets.get(category, 0)

                # סינון הוצאות מאותה קטגוריה בחודש הנוכחי
                year, month = date.year, date.month
                month_str = f"{year}-{month:02d}"
                month_transactions = filter_transactions_by_month(month_str)
                month_expenses = month_transactions[
                    (month_transactions['type'] == 'expense') &
                    (month_transactions['category'] == category)
                    ]

                total_spent = month_expenses['amount'].sum()

                if budget > 0 and total_spent > budget:
                    st.warning(
                        f"שים לב! חרגת מהתקציב בקטגוריה {category}. תקציב: {budget:,.0f} ₪, הוצאה מצטברת: {total_spent:,.0f} ₪")

                st.success(f"ההוצאה נוספה בהצלחה! סכום: {amount:,.0f} ₪")

# דף הגדרות תקציב
elif st.session_state.view == 'הגדרות תקציב':
    st.markdown('<h1 class="main-header">הגדרת תקציב חודשי</h1>', unsafe_allow_html=True)

    # הצגת חודש נוכחי
    year, month = map(int, st.session_state.month_filter.split('-'))
    month_name = calendar.month_name[month]
    st.markdown(f'<h2 class="sub-header">הגדרות תקציב ל-{month_name} {year}</h2>', unsafe_allow_html=True)

    # יצירת מסגרת לעדכון תקציב
    with st.form("budget_form"):
        # יצירת שדות עבור כל קטגוריית הוצאה
        budget_values = {}

        for category in st.session_state.categories['expense']:
            current_budget = st.session_state.budgets.get(category, 0)
            budget_values[category] = st.number_input(
                f"תקציב עבור {category} (₪)",
                min_value=0.0,
                value=float(current_budget),
                step=100.0
            )

        # כפתור שמירה
        submitted = st.form_submit_button("שמור תקציב")

        if submitted:
            # עדכון התקציבים
            st.session_state.budgets = budget_values
            st.success("התקציב עודכן בהצלחה!")

    # הצגת תרשים התפלגות תקציב
    st.markdown('<h3 class="sub-header">התפלגות התקציב</h3>', unsafe_allow_html=True)

    # סינון קטגוריות עם תקציב
    budget_data = {k: v for k, v in st.session_state.budgets.items() if v > 0}

    if len(budget_data) > 0:
        budget_df = pd.DataFrame({
            'category': list(budget_data.keys()),
            'amount': list(budget_data.values())
        })

        # יצירת תרשים עוגה
        fig = px.pie(
            budget_df,
            values='amount',
            names='category',
            title='התפלגות התקציב לפי קטגוריה',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        st.plotly_chart(fig, use_container_width=True)

        # סך כל התקציב
        total_budget = sum(budget_data.values())
        st.markdown(f"**סך כל התקציב החודשי:** {total_budget:,.0f} ₪")
    else:
        st.info("לא הוגדר תקציב לאף קטגוריה")

# דף עסקאות
elif st.session_state.view == 'עסקאות':
    st.markdown('<h1 class="main-header">ניהול עסקאות</h1>', unsafe_allow_html=True)

    # הצגת חודש נוכחי
    year, month = map(int, st.session_state.month_filter.split('-'))
    month_name = calendar.month_name[month]
    st.markdown(f'<h2 class="sub-header">עסקאות לחודש {month_name} {year}</h2>', unsafe_allow_html=True)

    if len(filtered_transactions) > 0:
        # בחירת סוג עסקאות להצגה
        transaction_type = st.radio(
            "סוג עסקאות:",
            ["הכל", "הכנסות", "הוצאות"],
            horizontal=True
        )

        # סינון לפי סוג
        if transaction_type == "הכנסות":
            display_transactions = filtered_transactions[filtered_transactions['type'] == 'income']
        elif transaction_type == "הוצאות":
            display_transactions = filtered_transactions[filtered_transactions['type'] == 'expense']
        else:
            display_transactions = filtered_transactions

        # מיון לפי תאריך
        display_transactions = display_transactions.sort_values('date', ascending=False)

        # יצירת טבלה להצגה
        display_df = display_transactions[['date', 'amount', 'category', 'description', 'type']].copy()

        # הוספת עמודה לפורמט מספרי
        display_df['formatted_amount'] = display_df.apply(
            lambda row: f"+{row['amount']:,.0f} ₪" if row['type'] == 'income' else f"-{row['amount']:,.0f} ₪",
            axis=1
        )

        # הוספת עמודה לסוג בעברית
        display_df['type_hebrew'] = display_df['type'].map({'income': 'הכנסה', 'expense': 'הוצאה'})

        # עיצוב הטבלה
        st.dataframe(
            display_df[['date', 'formatted_amount', 'category', 'description', 'type_hebrew']]
            .style
            .format({'date': lambda x: x.strftime('%d/%m/%Y')})
            .applymap(lambda x: 'color: #2E7D32' if 'הכנסה' in str(x) else 'color: #C62828', subset=['type_hebrew'])
            .set_properties(**{'text-align': 'center'})
            .hide_index()
            .set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold')]},
            ]),
            height=400
        )

        # קישור להורדת נתונים
        download_href = download_csv(display_transactions)
        st.markdown(download_href, unsafe_allow_html=True)

        # אפשרות למחיקת עסקאות
        with st.expander("מחיקת עסקאות"):
            st.warning("שים לב! מחיקת עסקאות היא פעולה בלתי הפיכה")

            # בחירת עסקה למחיקה
            transaction_options = []
            for _, row in display_transactions.iterrows():
                amount_text = f"+{row['amount']:,.0f}" if row['type'] == 'income' else f"-{row['amount']:,.0f}"
                option_text = f"{row['date'].strftime('%d/%m/%Y')} | {amount_text} ₪ | {row['description']}"
                transaction_options.append((option_text, row['id']))

            # יצירת אפשרויות בחירה
            option_texts = [t[0] for t in transaction_options]
            option_ids = [t[1] for t in transaction_options]

            selected_idx = st.selectbox("בחר עסקה למחיקה:", range(len(option_texts)),
                                        format_func=lambda i: option_texts[i])
            selected_id = option_ids[selected_idx]

            if st.button("מחק עסקה"):
                # מחיקת העסקה מהמסד
                st.session_state.transactions = st.session_state.transactions[
                    st.session_state.transactions['id'] != selected_id]
                st.success("העסקה נמחקה בהצלחה!")
                st.rerun()
    else:
        st.info("אין עסקאות להצגה בחודש זה")

# ריצה ראשונית - טעינת נתוני דוגמה אוטומטית
if len(st.session_state.transactions) == 0 and 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True
    load_sample_data()

    # הצגת הודעת ברוכים הבאים בפעם הראשונה
    welcome_container = st.empty()
    welcome_container.success("""
    ## ברוכים הבאים ל-RiseUp!

    האפליקציה נטענה עם נתוני דוגמה כדי שתוכל להתרשם מהפונקציונליות.

    * נווט בין דפים שונים באמצעות הכפתורים בסרגל הצד
    * הוסף הכנסות והוצאות חדשות
    * הגדר תקציב לקטגוריות השונות
    * צפה בדוחות וניתוחים

    בהצלחה בניהול התקציב!
    """)
