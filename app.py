import streamlit as st
import time
import pandas as pd
import openai
import requests
import re

# Set up OpenAI API client
openai.api_key = st.secrets["API_KEY"]


# function to get list of tasks
def grab_tasks():
    #st.session_state.session_tasks = test_list
    st.session_state.flow = 1

    # Generate real-world learning tasks

    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""You are a professional {st.session_state.profession} with several
             decades of work experience working in {st.session_state.industry}."""},
            {"role": "user", "content": f"""I want you to generate a numbered list of {st.session_state.task_num}
             real-world tasks related to the theme of {st.session_state.simulation_theme} that would
              require the following skills to accomplish successfully: {st.session_state.learning_objectives}

              For each task, provide a roughly 50 word description of the task."""}
        ],
        temperature=0.5
    )

    real_world_tasks = completions.choices[0]['message']['content']
    real_world_tasks = real_world_tasks.replace("/n", "").strip()
    st.session_state.session_tasks = re.split('\d\.', real_world_tasks)

# function to generate description for task

def grab_text(task_num):
    #st.session_state.session_text = test_text
    st.session_state.flow = 2

    if task_num == "0":
        task_desc = st.session_state.session_tasks[int(st.session_state.task)]
    else:
        st.session_state.task = task_num
        task_desc = st.session_state.session_tasks[int(task_num)]

    #Grab learning task description for the scenario



    # Generate learning task scenario
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""You are a master storyteller and and learning design expert helping
             to develop an authentic training simulation to teach following learning tasks: {task_desc}"""},
            {"role": "user", "content": f""" 
            
              To be engaging to learners, this simulation should follow the formula of a good story
              and place’s the student in the role of story protagonist. Provide the following:
              
              1. Generate a background story of at least 200 words to create the setting for
               the learning task. This should be in the style of {st.session_state.simulation_style} with the theme of
                {st.session_state.simulation_theme}.
                
              2. In at least 150 words, describe a mysterious, dangerous, or catastrophic problem that necessitates
               that the learner accomplish the learning task.
                          
                           
             3. Create a table of at least 5 chronologically ordered steps the student will need to
              complete in order to successful accomplish the learning task with each step described 
              within the context of the story and at least 50 words long.
              """}
        ],
        temperature=0.7
    )

    simulation_text = response.choices[0]['message']['content']
    st.session_state.scenario_text = simulation_text.replace("/n", "").strip()

    second_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""You are a master storyteller and and learning design expert."""},
            {"role": "assistant", "content": st.session_state.scenario_text},
            {"role": "user", "content": f""" 
            
            For each of the steps in the previous response, provide the following additional details:

             1. A 100 word description of that task in the context of the simulation narrative.
             2. Two reflection questions to assess student knowledge and meta-cognition as they progress
              through the simulation.
             3. Describe a potential way something can go wrong with the step within the context of the story and
             a question to ask the student

            """}
        ],
        temperature=0.7
    )

    simulation_ques = second_response.choices[0]['message']['content']
    st.session_state.simulation_ques = simulation_ques.replace("/n", "").strip()


def get_data():

    st.session_state.flow = 3

    data_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "assistant", "content": st.session_state.scenario_text},
            {"role": "user", "content": f"""Create a sample dataset consisting of 30 rows for the 
            prior scenario."""}
        ],
        temperature=0.7
    )

    st.session_state.data_output = data_response.choices[0]['message']['content']


def return_to_tasks():
    st.session_state.flow = 1

def return_to_generator():
    st.session_state.flow = 0


if 'flow' not in st.session_state or st.session_state.flow == 0:
    st.session_state.flow = 0

    st.title("Learning Task Idea Generator :bulb:")

    st.markdown("### Greetings, let's create some cool learning task ideas!")


    # Get user input
    st.session_state.profession = st.text_input("What is the job? :female-construction-worker:", "data scientist")
    st.session_state.industry = st.text_input("Should it be industry specific? :school::", "multiple industries")
    st.session_state.learning_objectives = st.text_input("List the activity learning objectives: :pencil:",
                                        "build and evaluate a linear regression model")

    st.session_state.task_num = st.number_input("How many learning task ideas to suggest?", min_value=1, max_value=10, value=5)
    st.session_state.simulation_theme = st.text_input("What is theme of simulation/case study? :flying_saucer:", "space disaster")
    st.session_state.simulation_style = st.text_input("What style should the simulation follow? :movie_camera:", "best-selling novel")

    st.button("Get me some task ideas!", on_click=grab_tasks, args="")

if st.session_state.flow == 1:
    #st.experimental_rerun()
    st.write("Here are some task ideas:")
    for count, item in enumerate(st.session_state.session_tasks):
        if count > 0:
            st.write(item)
            st.button(f"View a scenario for task number {count}", on_click=grab_text, args=f"{count}")

    st.text("")
    st.text("")
    st.button("Roll the dice! (Give me more task ideas.) ", on_click=grab_tasks, args="")
    st.button("Go back to task generator.", on_click=return_to_generator, args="")

if st.session_state.flow == 2:
    st.markdown(f"**Here's an simulation outline for following task:** {st.session_state.session_tasks[int(st.session_state.task_num)]}")
    st.text("")
    st.markdown("**:blue[Background, Problem, and Task Steps:]**")
    st.markdown(st.session_state.scenario_text)
    st.text("")
    st.markdown("**:blue[Step Details & Reflection Questions:]**")
    st.markdown(st.session_state.simulation_ques)
    st.text("")
    st.markdown("""----------------------------------------------------------""")
    st.button("Need Data?", on_click=get_data, args="")
    st.markdown("""----------------------------------------------------------""")
    st.button("Roll the dice! (Create another scenario for the task idea) ", on_click=grab_text, args="0")
    st.button("Go back to task list.", on_click=return_to_tasks, args="")
    st.button("Go back to task generator.", on_click=return_to_generator, args="")

if st.session_state.flow == 3:
    st.markdown(f"**Here's an simulation outline for following task:** {st.session_state.session_tasks[int(st.session_state.task_num)]}")
    st.text("")
    st.markdown("**:blue[Background, Problem, and Task Steps:]**")
    st.markdown(st.session_state.scenario_text)
    st.text("")
    st.markdown("**:blue[Step Details & Reflection Questions:]**")
    st.markdown(st.session_state.simulation_ques)
    st.text("")
    st.markdown("**:blue[Here's some data:]**")
    st.markdown(st.session_state.data_output)
    st.text("")
    st.markdown("""----------------------------------------------------------""")
    st.button("Roll the dice! (Create another scenario for the task idea) ", on_click=grab_text, args="0")
    st.button("Go back to task list.", on_click=return_to_tasks, args="")
    st.button("Go back to task generator.", on_click=return_to_generator, args="")





