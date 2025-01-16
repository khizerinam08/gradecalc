import streamlit as st

def validate_weightages(weights):
    return abs(sum(weights) - 100) < 0.001

st.title("Grade Calculator")

# Get number of sections
num_sections = st.number_input("How many assessment sections?", 
                             min_value=1, max_value=10, value=4, step=1)

if num_sections:
    # Initialize lists to store data
    section_names = []
    weightages = []
    your_scores = []
    class_averages = []
    
    # Create columns for inputs
    col1, col2, col3, col4 = st.columns(4)
    
    # Get section details
    with col1:
        st.subheader("Section Names")
        for i in range(num_sections):
            name = st.text_input(f"Section {i+1} name", key=f"name_{i}")
            section_names.append(name)
            
    with col2:
        st.subheader("Weightages (%)")
        for i in range(num_sections):
            weight = st.number_input(f"Weight {i+1}", 
                                   min_value=0.0, max_value=100.0, 
                                   key=f"weight_{i}")
            weightages.append(weight)
            
    with col3:
        st.subheader("Your Scores (%)")
        for i in range(num_sections):
            score = st.number_input(f"Score {i+1}", 
                                  min_value=0.0, max_value=100.0, 
                                  key=f"score_{i}")
            your_scores.append(score)
            
    with col4:
        st.subheader("Class Averages (%)")
        for i in range(num_sections):
            avg = st.number_input(f"Class Average {i+1}", 
                                min_value=0.0, max_value=100.0, 
                                key=f"avg_{i}")
            class_averages.append(avg)
    
    # Calculate aggregates if all inputs are valid
    if all(section_names) and validate_weightages(weightages):
        your_aggregate = sum(s * w / 100 for s, w in zip(your_scores, weightages))
        class_aggregate = sum(a * w / 100 for a, w in zip(class_averages, weightages))
        
        st.divider()
        st.subheader("Results")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Your Aggregate", f"{your_aggregate:.2f}%")
        with col2:
            st.metric("Class Aggregate", f"{class_aggregate:.2f}%")
            
        # Show detailed breakdown
        st.write("Detailed Breakdown:")
        for name, weight, score, avg in zip(section_names, weightages, 
                                          your_scores, class_averages):
            st.write(f"**{name}** (Weight: {weight}%)")
            st.write(f"Your Score: {score}% | Class Average: {avg}%")
    
    elif not validate_weightages(weightages):
        st.error("Weightages must sum to 100%")
