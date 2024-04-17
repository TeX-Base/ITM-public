import pickle
from pprint import pprint, pformat


# Specify the path to your pickle file
file_path = "components/probe_dumper/tmp/foo.pkl"

# Open the pickle file in read mode
with open(file_path, "rb") as file:
    # Load the contents of the pickle file
    data = pickle.load(file)

# Print the contents
choices = data.decisions_presented
new_cases = data.explanation.new_cases
minDecision = data.explanation.minDecision
minDistance = data.explanation.minDistance
choice_justifications = minDecision.justifications
scenario_description = data.scenario_description

pprint(scenario_description, width=160)

print("\nChoices:")
for choice in choices:
    for options in choice:
        pprint(options.value.name + " " + options.value.params["casualty"])
        
print("\nDecision:")
pprint(minDecision.value.name)
print()
pprint(choice_justifications)
#for justification in choice_justifications:
#    pprint(justification['DECISION_JUSTIFICATION_ENGLISH'])
    # pprint(justification['DECISION_JUSTIFICATION_VALUE'])

#for case in new_cases:
#    pprint(case)
    

    