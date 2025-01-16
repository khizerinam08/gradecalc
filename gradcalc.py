import streamlit as st
import re

st.title("Course Aggregate Calculator")
st.write("""This calculator shows how much each assessment type contributes to your final grade.
Enter your assessment data below to see the breakdown.""")

def parse_input_text(raw_text):
    data = []
    current_section = None
    weightage = None

    # Regex patterns
    section_pattern = re.compile(r"^(\w+(?:\s\w+)*)\s(\d+\.?\d*)\s%$", re.M)
    percentage_pattern = re.compile(r"^(\d+\.?\d*)$", re.M)
    assessment_pattern = re.compile(
        r"^(.*?)\t(\d+\.?\d*)\t(\d+\.?\d*)\t(\d+\.?\d*)\t(\d+\.?\d*)$", re.M
    )

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        
        section_match = section_pattern.match(line)
        if section_match:
            current_section = {
                "name": section_match.group(1),
                "weightage": float(section_match.group(2)),
                "direct_percentage": None,
                "assessments": []
            }
            data.append(current_section)
            i += 1
            
            if i < len(lines):
                percentage_match = percentage_pattern.match(lines[i])
                if percentage_match:
                    current_section["direct_percentage"] = float(percentage_match.group(1))
                    i += 1
                    
            while i < len(lines):
                if "Assessment" in lines[i]:
                    i += 1
                    continue
                    
                assessment_match = assessment_pattern.match(lines[i])
                if assessment_match:
                    assessment = {
                        "name": assessment_match.group(1),
                        "max_mark": float(assessment_match.group(2)),
                        "obtained_mark": float(assessment_match.group(3)),
                        "class_average": float(assessment_match.group(4)),
                        "percentage": float(assessment_match.group(5))
                    }
                    current_section["assessments"].append(assessment)
                    i += 1
                else:
                    break
        else:
            i += 1
            
    return data

def calculate_contribution(section, component_weight=1.0):
    """Calculate how much this section contributed to final grade"""
    section_weight = section["weightage"] / 100
    
    if section["direct_percentage"] is not None:
        percentage = section["direct_percentage"]
    elif section["assessments"]:
        percentage = sum(a["obtained_mark"] / a["max_mark"] * 100 
                        for a in section["assessments"]) / len(section["assessments"])
    else:
        return 0, 0
    
    actual_contribution = percentage * section_weight * component_weight
    max_possible = 100 * section_weight * component_weight
    
    return actual_contribution, max_possible

# Weight configuration
st.subheader("Component Weights")
col1, col2 = st.columns(2)
with col1:
    theory_weight = st.number_input("Theory Weight (%)", min_value=0.0, max_value=100.0, value=70.0, step=1.0)
with col2:
    lab_weight = st.number_input("Lab Weight (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)

total_weight = theory_weight + lab_weight
if total_weight != 100:
    st.warning(f"⚠️ Total weight should be 100%. Current total: {total_weight}%")

theory_weight_decimal = theory_weight / 100
lab_weight_decimal = lab_weight / 100

# Input areas
st.subheader(f"Theory Component ({theory_weight}%)")
theory_text = st.text_area("Paste the theory assessment details here:", height=300)

st.subheader(f"Lab Component ({lab_weight}%)")
lab_text = st.text_area("Paste the lab assessment details here:", height=300)

if theory_text or lab_text:
    try:
        st.divider()
        st.subheader("Percentage Contribution Breakdown")
        
        total_contribution = 0
        
        # Process theory component
        if theory_text:
            theory_data = parse_input_text(theory_text)
            st.write("### Theory Component Breakdown")
            
            theory_contribution = 0
            for section in theory_data:
                contribution, max_possible = calculate_contribution(section, theory_weight_decimal)
                theory_contribution += contribution
                
                # Calculate what percentage of the total possible marks this represents
                percentage_of_total = (contribution / max_possible * 100) if max_possible > 0 else 0
                
                # Display the contribution
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{section['name']} ({section['weightage']}%)**")
                with col2:
                    st.write(f"Contributed: {contribution:.2f} marks")
                with col3:
                    st.write(f"({percentage_of_total:.2f}% of possible {max_possible:.2f})")
            
            st.write(f"**Total Theory Contribution: {theory_contribution:.2f}%**")
            total_contribution += theory_contribution
        
        # Process lab component
        if lab_text:
            lab_data = parse_input_text(lab_text)
            st.write("### Lab Component Breakdown")
            
            lab_contribution = 0
            for section in lab_data:
                contribution, max_possible = calculate_contribution(section, lab_weight_decimal)
                lab_contribution += contribution
                
                # Calculate what percentage of the total possible marks this represents
                percentage_of_total = (contribution / max_possible * 100) if max_possible > 0 else 0
                
                # Display the contribution
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{section['name']} ({section['weightage']}%)**")
                with col2:
                    st.write(f"Contributed: {contribution:.2f} marks")
                with col3:
                    st.write(f"({percentage_of_total:.2f}% of possible {max_possible:.2f})")
            
            st.write(f"**Total Lab Contribution: {lab_contribution:.2f}%**")
            total_contribution += lab_contribution
        
        # Show final total
        if theory_text and lab_text:
            st.divider()
            st.subheader("Final Grade")
            st.write(f"**Total Grade: {total_contribution:.2f}%**")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please make sure the input format matches the example.")