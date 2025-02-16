import streamlit as st
import pandas as pd
import random
import hmac
import os

# MUST be the very first Streamlit command.
st.set_page_config(page_title="Cute Practice Test", layout="centered")

# Password verification function
def check_password():
    """Returns `True` if the user entered the correct password."""
    def password_entered():
        """Checks whether the entered password is correct."""
        # Get password from secrets or environment variable
        stored_password = os.getenv("STREAMLIT_PASSWORD", st.secrets.get("password"))

        if stored_password is None:
            st.error("No password found! Please set it in Streamlit secrets or an environment variable.")
            return

        if hmac.compare_digest(st.session_state["password"], stored_password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Remove the password from session state
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct"):
        return True
    else:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        if st.session_state.get("password_correct") == False:
            st.error("Incorrect password")
        return False

if check_password():


    st.markdown(
        """
        <style>
        /* Base Page Styling */
        body {
            background-color: #F9F6FB !important;  /* Light pastel background for a gentle feel */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            color: #333 !important;
        }

        /* Header Styling */
        .header {
            background-color: #5F259F !important;  /* Databricks-inspired purple */
            color: #FFFFFF !important;
            padding: 1.2em !important;
            border-radius: 10px !important;
            text-align: center !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
            margin-bottom: 20px !important;
        }

        /* Card Component Styling */
        .card {
            background-color: #FFFFFF !important;
            border: 1px solid #E0E0E0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            margin: 15px 0 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
            transition: transform 0.2s, box-shadow 0.2s !important;
        }
        .card:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.12) !important;
        }

        /* Link Styling */
        a {
            color: #5F259F !important;
            text-decoration: none !important;
            border-bottom: 1px dashed #5F259F !important;
            transition: color 0.3s, border-bottom-color 0.3s !important;
        }
        a:hover {
            color: #7A3EBC !important;
            border-bottom-color: #7A3EBC !important;
        }

        /* Button Styling */
        .btn {
            background-color: #5F259F !important;
            color: #FFF !important;
            padding: 10px 20px !important;
            border: none !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            transition: background-color 0.3s, transform 0.2s !important;
        }
        .btn:hover {
            background-color: #7A3EBC !important;
            transform: scale(1.03) !important;
        }
        
        /* Miscellaneous Styling */
        .footer {
            font-size: 0.9em !important;
            color: #777 !important;
            text-align: center !important;
            padding: 10px 0 !important;
            margin-top: 30px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # Display a cute banner image.
    st.image("https://media.tenor.com/qJRMLPlR3_8AAAAj/maxwell-cat.gif")

    # Initialize session state.
    if "test_started" not in st.session_state:
        st.session_state.test_started = False

    # Use an empty container to hold the settings form.
    settings_container = st.empty()

    # --- SCREEN 1: Test Settings ---
    if not st.session_state.test_started:
        with settings_container:
            st.header("Test Settings")
            st.markdown("Set up your quiz below. Once you hit **Start Test**, your quiz will begin!")
            
            # File uploader (optional): if left empty, the default workbook is used.
            uploaded_file = st.file_uploader(
                "Upload your questions file (CSV, TSV, or Excel) - leave empty to use default workbook",
                type=["csv", "tsv", "xlsx", "xls"]
            )
            
            df = None
            if uploaded_file is not None:
                try:
                    filename = uploaded_file.name.lower()
                    if filename.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(uploaded_file)
                    else:
                        df = pd.read_csv(uploaded_file, sep=None, engine='python')
                except Exception as e:
                    st.error("Error reading uploaded file: " + str(e))
            else:
                            # Load the default workbook.
                default_path = "dbdea_q_and_a.xlsx"
                try:
                    df = pd.read_excel(default_path)
                    st.info("Using default workbook.")
                except Exception as e:
                    st.error("Error reading default file: " + str(e))
            
            if df is not None:
                # Check for the category column.
                if 'category' not in df.columns:
                    st.error("The provided file does not contain a 'category' column.")
                    st.stop()
                
                # Get unique, sorted categories.
                categories = sorted(df['category'].dropna().unique())
                
                # Settings form for additional inputs.
                with st.form("settings_form", clear_on_submit=True):
                    num_questions = st.number_input("Number of Questions", min_value=1, value=5, step=1)
                    selected_category = st.selectbox("Select Category", options=categories)
                    submitted_settings = st.form_submit_button("Start Test")
                    
                    if submitted_settings:
                        # Filter questions by the selected category.
                        df_category = df[df['category'] == selected_category]
                        
                        # Convert to a list of question dictionaries.
                        questions = df_category.to_dict("records")
                        # Clean up any empty 'e' keys.
                        for q in questions:
                            if "e" in q and (pd.isna(q["e"]) or str(q["e"]).strip() == ""):
                                q.pop("e")
                        
                        if len(questions) == 0:
                            st.error(f"No questions available for the category '{selected_category}'. Please choose a different category or file.")
                            st.stop()
                        
                        if num_questions > len(questions):
                            st.warning("Requested number of questions exceeds available questions. Using all available questions.")
                            num_questions = len(questions)
                        
                        # Randomize question order.
                        random_questions = random.sample(questions, num_questions)
                        
                        # Save settings in session state.
                        st.session_state.random_questions = random_questions
                        st.session_state.num_questions = num_questions
                        st.session_state.test_started = True
                        
                        # Clear the settings container.
                        settings_container.empty()

    # --- SCREEN 2: The Quiz/Test ---
    if st.session_state.get("test_started"):
        st.header("Your Test")
        st.markdown("Answer the questions below and click **Submit Test** when you're done. Good luck!")
        
        with st.form("test_form"):
            user_answers = {}
            
            for i, q in enumerate(st.session_state.random_questions):
                st.markdown(f"### Question {i+1}")
                st.markdown(q["questions"])
                
                # Build answer options.
                option_letters = []
                option_texts = []
                for letter in ["a", "b", "c", "d", "e"]:
                    if letter in q and str(q[letter]).strip() != "":
                        option_letters.append(letter.upper())
                        option_texts.append(f"{letter.upper()}: {q[letter]}")
                
                correct_answer = str(q["answers"]).strip().upper()
                if len(correct_answer) == 1:
                    answer = st.radio("Select one:", option_texts, key=f"q{i}")
                    user_answers[i] = answer.split(":")[0].strip()
                else:
                    st.markdown("Select all that apply:")
                    selections = []
                    for letter, text in zip(option_letters, option_texts):
                        if st.checkbox(text, key=f"q{i}_{letter}"):
                            selections.append(letter)
                    user_answers[i] = sorted(selections)
            
            submitted_test = st.form_submit_button("Submit Test")
        
        if submitted_test:
            st.balloons()
            st.markdown("---")
            st.header("Results")
            score = 0
            
            for i, q in enumerate(st.session_state.random_questions):
                correct = sorted(list(str(q["answers"]).strip().upper()))
                response = user_answers.get(i)
                # Normalize a single-answer response to a list.
                if isinstance(response, str):
                    response_list = [response]
                else:
                    response_list = sorted(response)
                
                if response_list == correct:
                    st.success(f"Question {i+1}: Correct!")
                    score += 1
                else:
                    st.error(f"Question {i+1}: Incorrect. Correct answer: {', '.join(correct)}")

            st.markdown("---")
            st.info(f"Your score: {score} out of {st.session_state.num_questions}")
            st.image("https://media.tenor.com/J2SMf2oW7XkAAAAi/cat-stare.gif", use_container_width=True)
        
        # "Go Back" button to return to test settings.
        if st.button("Go Back to Test Settings"):
            # Clear session state so that the settings screen reappears.
            for key in list(st.session_state.keys()):
                del st.session_state[key]
