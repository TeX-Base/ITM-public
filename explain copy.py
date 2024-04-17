import pickle
from pprint import pprint, pformat
import pandas

# Specify the path to your pickle file
file_path = "components/probe_dumper/tmp/MetricsEval.MD1-Urban.pkl"

# Open the pickle file in read mode
with open(file_path, "rb") as file:
    # Load the contents of the pickle file
    data = pickle.load(file)

# Print the contents
new_cases = data.explanation.new_cases
#choice_justifications = minDecision.justifications
scenario_description = data.scenario_description
minDecision = data.explanation.minDecision
minDistance = data.explanation.minDistance
top_decisions = data.explanation.topDecisions


print("Scenario Description:")
print(scenario_description)

print("Example Decision:")
#print(minDecision.value.name + " " + minDecision.value.params["casualty"])
#print("Distance from estimated: " + str(minDistance.round(2)))

#minDecision_metrics = pandas.DataFrame(minDecision.metrics, index=[0])
example_decision = new_cases[6]
print(example_decision["treatment"])

print("\nNearest cases from case base:")
for top_decision in top_decisions:
    print("Case No. " + str(top_decision[1]["index"]) + " " +top_decision[1]["action"])

# select the first decision from the top decisions as an example
example_decision = top_decisions[0][1]
print("\nExample Decision:")

