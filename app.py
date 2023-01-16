import streamlit as st
import time
import pandas as pd
import openai
import requests
import re

# Set up OpenAI API client
openai.api_key = st.secrets["API_KEY"]


test_list = ["Task Number One", "Task Number Two", "Task Number Three", "Task Number Four"]
test_text = "Yes, this is working now!"


def grab_tasks():
    #st.session_state.session_tasks = test_list
    st.session_state.flow = 1

    # Generate real-world learning tasks
    model_engine = "text-davinci-003"
    prompt = (
        f"Provide {st.session_state.task_num} real-world tasks ideas for a {st.session_state.profession} working in {st.session_state.industry}. Each task description should be 2-3 sentences long and require an employee to demonstrate the following skills:{st.session_state.learning_objectives}.")
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    real_world_tasks = completions.choices[0].text
    real_world_tasks = real_world_tasks.replace("/n", "").strip()
    st.session_state.session_tasks = re.split('\d\.', real_world_tasks)

def grab_text(task_num):
    #st.session_state.session_text = test_text
    st.session_state.flow = 2
    st.session_state.task = task_num

    #Grab learning task description for the scenario

    task_desc = st.session_state.session_tasks[int(task_num)]

    # Generate learning task scenario
    model_engine = "text-davinci-003"
    prompt = (
        f"Use the following task description to 1) create a real-world background story at least two paragraphs long and including several characters with unusual names, 2) generate a list of 8-10 detailed steps someone would need to do to accomplish the task, 3) Include two reflective questions for each step that a boss might ask to assess an employee's understanding. Here is the task description: {task_desc} ")
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    real_world_tasks = completions.choices[0].text
    st.session_state.session_text = real_world_tasks.replace("/n", "").strip()

def return_to_tasks():
    st.session_state.flow = 1

def return_to_generator():
    st.session_state.flow = 0


#st.write(st.session_state)

if 'flow' not in st.session_state or st.session_state.flow == 0:
    st.session_state.flow = 0

    st.title("Learning Task Generator")

    st.markdown("### Greetings, let's create some real-world learning task ideas!")


    # Get user input
    st.session_state.profession = st.text_input("What is the job?", "data scientist")
    st.session_state.industry = st.text_input("What is the industry?:", "forestry")
    st.session_state.learning_objectives = st.text_input("List the activity learning objectives:",
                                        "create a random forest machine learning model, evaluate the effectiveness of a random forest machine learning model, identify the most important variables in a random forest machine learning model")

    st.session_state.task_num = st.number_input("How many tasks?", min_value=1, max_value=10)
    st.button("Get task ideas:", on_click=grab_tasks, args="")

if st.session_state.flow == 1:
    #st.experimental_rerun()
    st.write("Here are some tasks:")
    for count, item in enumerate(st.session_state.session_tasks):
        if count > 0:
            st.write(item)
            st.button(f"View a scenario for task number {count}", on_click=grab_text, args=f"{count}")

if st.session_state.flow == 2:
    st.markdown(f"**Here is your task description for the following task:** {st.session_state.session_tasks[int(st.session_state.task_num)]}")

    st.markdown(st.session_state.session_text)

    st.button("Go back to task list.", on_click=return_to_tasks, args="")
    st.button("Go back to task generator.", on_click=return_to_generator, args="")





