import streamlit as st
import re

st.title("Course Aggregate Calculator")

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
        
        # Check for section header
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
            
            # Check next line for direct percentage
            if i < len(lines):
                percentage_match = percentage_pattern.match(lines[i])
                if percentage_match:
                    current_section["direct_percentage"] = float(percentage_match.group(1))
                    i += 1
                    
            # Look for assessments
            while i < len(lines):
                if "Assessment" in lines[i]:  # Skip header row
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

def calculate_component_aggregate(data):
    user_aggregate = 0
    class_aggregate = 0

    for section in data:
        weightage = section["weightage"] / 100

        # If there's a direct percentage, use it
        if section["direct_percentage"] is not None:
            user_percentage = section["direct_percentage"]
            # For class average, use the assessment averages if available
            if section["assessments"]:
                class_percentage = sum(a["class_average"] / a["max_mark"] * 100 
                                    for a in section["assessments"]) / len(section["assessments"])
            else:
                class_percentage = user_percentage  # Fallback if no assessments
        
        # Otherwise calculate from assessments
        elif section["assessments"]:
            user_percentage = sum(a["obtained_mark"] / a["max_mark"] * 100 
                                for a in section["assessments"]) / len(section["assessments"])
            class_percentage = sum(a["class_average"] / a["max_mark"] * 100 
                                 for a in section["assessments"]) / len(section["assessments"])
        else:
            continue  # Skip if no data available

        user_aggregate += user_percentage * weightage
        class_aggregate += class_percentage * weightage

    return user_aggregate, class_aggregate

# Weight configuration
st.subheader("Component Weights")
col1, col2 = st.columns(2)
with col1:
    theory_weight = st.number_input("Theory Weight (%)", min_value=0.0, max_value=100.0, value=70.0, step=1.0)
with col2:
    lab_weight = st.number_input("Lab Weight (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)

# Validate weights
total_weight = theory_weight + lab_weight
if total_weight != 100:
    st.warning(f"⚠️ Total weight should be 100%. Current total: {total_weight}%")

# Convert weights to decimals
theory_weight_decimal = theory_weight / 100
lab_weight_decimal = lab_weight / 100

# Create two text areas for theory and lab components
st.subheader(f"Theory Component ({theory_weight}%)")
theory_text = st.text_area("Paste the theory assessment details here:", height=300)

st.subheader(f"Lab Component ({lab_weight}%)")
lab_text = st.text_area("Paste the lab assessment details here:", height=300)

if theory_text or lab_text:
    try:
        # Initialize aggregates
        final_user_aggregate = 0
        final_class_aggregate = 0
        
        # Process theory component if provided
        if theory_text:
            theory_data = parse_input_text(theory_text)
            theory_user, theory_class = calculate_component_aggregate(theory_data)
            
            st.divider()
            st.subheader(f"Theory Results ({theory_weight}% of Total)")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Your Theory Aggregate", f"{theory_user:.2f}%")
            with col2:
                st.metric("Class Theory Aggregate", f"{theory_class:.2f}%")
                
            final_user_aggregate += theory_user * theory_weight_decimal
            final_class_aggregate += theory_class * theory_weight_decimal
            
            # Theory breakdown
            st.write("### Theory Breakdown")
            for section in theory_data:
                st.write(f"#### {section['name']} (Weight: {section['weightage']}%)")
                if section["direct_percentage"] is not None:
                    st.write(f"Direct Percentage: **{section['direct_percentage']}%**")
                if section["assessments"]:
                    st.write("Assessments:")
                    for assessment in section["assessments"]:
                        st.write(
                            f"- **{assessment['name']}**: "
                            f"Mark: {assessment['obtained_mark']}/{assessment['max_mark']}, "
                            f"Class Avg: {assessment['class_average']}, "
                            f"Percentage: {assessment['percentage']}%"
                        )
        
        # Process lab component if provided
        if lab_text:
            lab_data = parse_input_text(lab_text)
            lab_user, lab_class = calculate_component_aggregate(lab_data)
            
            st.divider()
            st.subheader(f"Lab Results ({lab_weight}% of Total)")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Your Lab Aggregate", f"{lab_user:.2f}%")
            with col2:
                st.metric("Class Lab Aggregate", f"{lab_class:.2f}%")
                
            final_user_aggregate += lab_user * lab_weight_decimal
            final_class_aggregate += lab_class * lab_weight_decimal
            
            # Lab breakdown
            st.write("### Lab Breakdown")
            for section in lab_data:
                st.write(f"#### {section['name']} (Weight: {section['weightage']}%)")
                if section["direct_percentage"] is not None:
                    st.write(f"Direct Percentage: **{section['direct_percentage']}%**")
                if section["assessments"]:
                    st.write("Assessments:")
                    for assessment in section["assessments"]:
                        st.write(
                            f"- **{assessment['name']}**: "
                            f"Mark: {assessment['obtained_mark']}/{assessment['max_mark']}, "
                            f"Class Avg: {assessment['class_average']}, "
                            f"Percentage: {assessment['percentage']}%"
                        )
        
        # Show final results if both components are provided
        if theory_text and lab_text:
            st.divider()
            st.subheader("Final Course Results")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Your Final Aggregate", f"{final_user_aggregate:.2f}%")
            with col2:
                st.metric("Class Final Aggregate", f"{final_class_aggregate:.2f}%")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please make sure the input format matches the example.")